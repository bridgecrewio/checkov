from __future__ import annotations

import itertools
import logging
import os
import re
from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import List, Any, TYPE_CHECKING, TypeVar, Generic, Dict

from checkov.common.graph.db_connectors.igraph.igraph_db_connector import IgraphConnector
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.util.tqdm_utils import ProgressBar

from checkov.common.graph.checks_infra.base_check import BaseGraphCheck
from checkov.common.output.report import Report
from checkov.runner_filter import RunnerFilter

if TYPE_CHECKING:
    from checkov.common.checks_infra.registry import Registry
    from checkov.common.graph.checks_infra.registry import BaseRegistry
    from checkov.common.graph.graph_manager import GraphManager  # noqa
    from checkov.common.typing import _CheckResult, LibraryGraphConnector

_GraphManager = TypeVar("_GraphManager", bound="GraphManager[Any, Any]|None")


def strtobool(val: str) -> int:
    """Convert a string representation of truth to true (1) or false (0).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return 1
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return 0
    else:
        raise ValueError("invalid boolean value %r for environment variable CKV_IGNORE_HIDDEN_DIRECTORIES" % (val,))


CHECKOV_CREATE_GRAPH = strtobool(os.getenv("CHECKOV_CREATE_GRAPH", "True"))
IGNORED_DIRECTORIES_ENV = os.getenv("CKV_IGNORED_DIRECTORIES", "node_modules,.terraform,.serverless")
IGNORE_HIDDEN_DIRECTORY_ENV = strtobool(os.getenv("CKV_IGNORE_HIDDEN_DIRECTORIES", "True"))

ignored_directories = IGNORED_DIRECTORIES_ENV.split(",")


class BaseRunner(ABC, Generic[_GraphManager]):
    check_type = ""
    definitions: dict[str, dict[str, Any] | list[dict[str, Any]]] | None = None
    raw_definitions: dict[str, list[tuple[int, str]]] | None = None
    context: dict[str, dict[str, Any]] | None = None
    breadcrumbs = None
    external_registries: list[BaseRegistry] | None = None
    graph_manager: _GraphManager | None = None
    graph_registry: Registry | None = None
    db_connector: LibraryGraphConnector

    def __init__(self, file_extensions: Iterable[str] | None = None, file_names: Iterable[str] | None = None):
        self.file_extensions = file_extensions or []
        self.file_names = file_names or []
        self.pbar = ProgressBar(self.check_type)
        db_connector_class: "type[NetworkxConnector | IgraphConnector]" = NetworkxConnector
        graph_framework = os.getenv("CHECKOV_GRAPH_FRAMEWORK", "NETWORKX")
        if graph_framework == "IGRAPH":
            db_connector_class = IgraphConnector
        elif graph_framework == "NETWORKX":
            db_connector_class = NetworkxConnector

        self.db_connector = db_connector_class()

    @abstractmethod
    def run(
            self,
            root_folder: str | None,
            external_checks_dir: list[str] | None = None,
            files: list[str] | None = None,
            runner_filter: RunnerFilter | None = None,
            collect_skip_comments: bool = True,
    ) -> Report | list[Report]:
        pass

    def should_scan_file(self, filename: str) -> bool:
        # runners that are always applicable can do nothing and be included
        if not self.file_extensions and not self.file_names:
            return True

        basename = os.path.basename(filename)
        if basename and self.file_names and basename in self.file_names:
            return True

        extension = os.path.splitext(filename)[1]
        if extension and self.file_extensions and extension in self.file_extensions:
            return True

        return False

    def set_external_data(
            self,
            definitions: dict[str, dict[str, Any] | list[dict[str, Any]]] | None,
            context: dict[str, dict[str, Any]] | None,
            breadcrumbs: dict[str, dict[str, Any]] | None,
            **kwargs: Any,
    ) -> None:
        self.definitions = definitions
        self.context = context
        self.breadcrumbs = breadcrumbs

    def set_raw_definitions(self, definitions_raw: dict[str, list[tuple[int, str]]] | None) -> None:
        self.definitions_raw = definitions_raw

    def populate_metadata_dict(self) -> None:
        return None

    def load_external_checks(self, external_checks_dir: List[str]) -> None:
        return None

    def get_graph_checks_report(self, root_folder: str, runner_filter: RunnerFilter) -> Report:
        return Report(check_type="not_defined")

    def run_graph_checks_results(self, runner_filter: RunnerFilter, report_type: str) -> dict[BaseGraphCheck, list[_CheckResult]]:
        checks_results: "dict[BaseGraphCheck, list[_CheckResult]]" = {}
        if not self.graph_manager or not self.graph_registry:
            # should not happen
            logging.warning("Graph components were not initialized")
            return checks_results

        for r in itertools.chain(self.external_registries or [], [self.graph_registry]):
            r.load_checks()
            registry_results = r.run_checks(self.graph_manager.get_reader_endpoint(), runner_filter, report_type)  # type:ignore[union-attr]
            checks_results = {**checks_results, **registry_results}
        # Filtering the checks now
        filtered_result: Dict[BaseGraphCheck, List[_CheckResult]] = {}
        for check, results in checks_results.items():
            filtered_result[check] = [result for result in results if runner_filter.should_run_check(
                check,
                check_id=check.id,
                file_origin_paths=[result.get("entity", {}).get(CustomAttributes.FILE_PATH, "")]
            )]

        return filtered_result


def filter_ignored_paths(
    root_dir: str,
    names: list[str] | list[os.DirEntry[str]],
    excluded_paths: list[str] | None,
    included_paths: Iterable[str] | None = None
) -> None:
    # we need to handle legacy logic, where directories to skip could be specified using the env var (default value above)
    # or a directory starting with '.'; these look only at directory basenames, not relative paths.
    #
    # But then any other excluded paths (specified via --skip-path or via the platform repo settings) should look at
    # the path name relative to the root folder. These can be files or directories.
    # Example: take the following dir tree:
    # .
    #   ./dir1
    #      ./dir1/dir33
    #      ./dir1/.terraform
    #   ./dir2
    #      ./dir2/dir33
    #      /.dir2/hello.yaml
    #
    # if excluded_paths = ['dir1/dir33', 'dir2/hello.yaml'], then we would scan dir1, but we would skip its subdirectories. We would scan
    # dir2 and its subdirectory, but we'd skip hello.yaml.

    # first handle the legacy logic - this will also remove files starting with '.' but that's probably fine
    # mostly this will just remove those problematic directories hardcoded above.
    included_paths = included_paths or []
    for entry in list(names):
        path = entry.name if isinstance(entry, os.DirEntry) else entry
        if path in ignored_directories:
            safe_remove(names, entry)
        if path.startswith(".") and IGNORE_HIDDEN_DIRECTORY_ENV and path not in included_paths:
            safe_remove(names, entry)

    # now apply the new logic
    # TODO this is not going to work well on Windows, because paths specified in the platform will use /, and
    #  paths specified via the CLI argument will presumably use \\
    if excluded_paths:
        compiled = []
        for p in excluded_paths:
            try:
                compiled.append(re.compile(p.replace(".terraform", r"\.terraform")))
            except re.error:
                # do not add compiled paths that aren't regexes
                continue
        for entry in list(names):
            path = entry.name if isinstance(entry, os.DirEntry) else entry
            full_path = os.path.join(root_dir, path)
            if any(pattern.search(full_path) for pattern in compiled) or any(p in full_path for p in excluded_paths):
                safe_remove(names, entry)


def safe_remove(names: list[Any], path: Any) -> None:
    if path in names:
        names.remove(path)

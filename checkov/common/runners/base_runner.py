from __future__ import annotations

import itertools
import logging
import os
import re
from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import List, Dict, Any, TYPE_CHECKING, TypeVar, Generic

from checkov.common.util.tqdm_utils import ProgressBar

from checkov.common.graph.checks_infra.base_check import BaseGraphCheck
from checkov.common.output.report import Report
from checkov.runner_filter import RunnerFilter

if TYPE_CHECKING:
    from checkov.common.checks_infra.registry import Registry
    from checkov.common.graph.checks_infra.registry import BaseRegistry
    from checkov.common.graph.graph_manager import GraphManager  # noqa

_GraphManager = TypeVar("_GraphManager", bound="GraphManager[Any]|None")


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
    definitions = None
    context: dict[str, dict[str, Any]] | None = None
    breadcrumbs = None
    external_registries: list[BaseRegistry] | None = None
    graph_manager: _GraphManager | None = None
    graph_registry: Registry | None = None

    def __init__(self, file_extensions: Iterable[str] | None = None, file_names: Iterable[str] | None = None):
        self.file_extensions = file_extensions or []
        self.file_names = file_names or []
        self.pbar = ProgressBar(self.check_type)

    @abstractmethod
    def run(
            self,
            root_folder: str | None,
            external_checks_dir: list[str] | None = None,
            files: list[str] | None = None,
            runner_filter: RunnerFilter = RunnerFilter(),
            collect_skip_comments: bool = True,
    ) -> Report:
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
            definitions: dict[str, dict[str, Any]] | None,
            context: dict[str, dict[str, Any]] | None,
            breadcrumbs: dict[str, dict[str, Any]] | None,
            **kwargs: Any,
    ) -> None:
        self.definitions = definitions
        self.context = context
        self.breadcrumbs = breadcrumbs

    def load_external_checks(self, external_checks_dir: List[str]) -> None:
        pass

    def get_graph_checks_report(self, root_folder: str, runner_filter: RunnerFilter) -> Report:
        pass

    def run_graph_checks_results(self, runner_filter: RunnerFilter) -> Dict[BaseGraphCheck, List[Dict[str, Any]]]:
        checks_results: Dict[BaseGraphCheck, List[Dict[str, Any]]] = {}

        if not self.graph_manager or not self.graph_registry:
            # should not happen
            logging.warning("Graph components were not initialized")
            return checks_results

        for r in itertools.chain(self.external_registries or [], [self.graph_registry]):
            r.load_checks()
            registry_results = r.run_checks(self.graph_manager.get_reader_endpoint(), runner_filter)  # type:ignore[union-attr]
            checks_results = {**checks_results, **registry_results}
        return checks_results


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
        compiled = [re.compile(p.replace(".terraform", r"\.terraform")) for p in excluded_paths]
        for entry in list(names):
            path = entry.name if isinstance(entry, os.DirEntry) else entry
            if any(pattern.search(os.path.join(root_dir, path)) for pattern in compiled):
                safe_remove(names, entry)


def safe_remove(names: list[Any], path: Any) -> None:
    if path in names:
        names.remove(path)

from __future__ import annotations

import fnmatch
import importlib
import importlib.util
import logging
import os
import sys
from abc import abstractmethod
from collections import defaultdict
from itertools import chain
from typing import Generator, Tuple, Dict, List, Optional, Any, TYPE_CHECKING

from checkov.common.models.enums import CheckResult
from checkov.common.typing import _SkippedCheck, _CheckResult
from checkov.runner_filter import RunnerFilter

if TYPE_CHECKING:
    from checkov.common.checks.base_check import BaseCheck


class BaseCheckRegistry:
    # NOTE: Needs to be static to because external check loading may be triggered by a registry to which
    #       checks aren't registered. (This happens with Serverless, for example.)
    __loading_external_checks = False  # noqa: CCE003
    __all_registered_checks: list[BaseCheck] = []  # noqa: CCE003

    def __init__(self, report_type: str) -> None:
        self.logger = logging.getLogger(__name__)
        # IMPLEMENTATION NOTE: Checks is used to directly access checks based on an specific entity
        self.checks: Dict[str, List[BaseCheck]] = defaultdict(list)
        # IMPLEMENTATION NOTE: When using a wildcard, every pattern needs to be checked. To reduce the
        #                      number of checks checks with the same pattern are grouped, which is the
        #                      reason to use a dict for this too.
        self.wildcard_checks: Dict[str, List[BaseCheck]] = defaultdict(list)
        self.check_id_allowlist: Optional[List[str]] = None
        self.report_type = report_type
        self.definitions_raw: list[tuple[int, str]] | None = None

    def register(self, check: BaseCheck) -> None:
        # IMPLEMENTATION NOTE: Checks are registered when the script is loaded
        #                      (see BaseResourceCheck.__init__() for the various frameworks). The only
        #                      difficultly with this process is that external checks need to be specially
        #                      identified for filter handling. That's why you'll see stateful setting of
        #                      RunnerFilters during load_external_checks.
        #                      Built-in checks are registered immediately at script start, before
        #                      external checks.
        if BaseCheckRegistry.__loading_external_checks:
            RunnerFilter.notify_external_check(check.id)

        for entity in check.supported_entities:
            checks = self.wildcard_checks if self._is_wildcard(entity) else self.checks
            if not any(c.id == check.id for c in checks[entity]):
                checks[entity].append(check)

        BaseCheckRegistry.__all_registered_checks.append(check)

    @staticmethod
    def get_all_registered_checks() -> List[BaseCheck]:
        return BaseCheckRegistry.__all_registered_checks

    @staticmethod
    def _is_wildcard(entity: str) -> bool:
        return "*" in entity or "?" in entity or ("[" in entity and "]" in entity)

    def get_check_by_id(self, check_id: str) -> Optional[BaseCheck]:
        return next(
            (check for check in chain(*self.checks.values(), *self.wildcard_checks.values()) if check.id == check_id),
            None,
        )

    def all_checks(self) -> Generator[Tuple[str, BaseCheck], None, None]:
        for entity, checks in self.checks.items():
            for check in checks:
                yield entity, check
        for entity, checks in self.wildcard_checks.items():
            for check in checks:
                yield entity, check

    @property
    def contains_wildcard(self) -> bool:
        return bool(self.wildcard_checks)

    def get_checks(self, entity: str) -> List[BaseCheck]:
        if not self.wildcard_checks:
            # Optimisation: When no wildcards are used, we can use the list in self.checks
            return self.checks.get(entity) or []
        else:
            res = self.checks[entity].copy() if entity in self.checks.keys() else []
            # check wildcards
            for pattern, checks in self.wildcard_checks.items():
                if entity and fnmatch.fnmatchcase(entity, pattern):
                    res += checks
            return res

    def set_checks_allowlist(self, runner_filter: RunnerFilter) -> None:
        if runner_filter.checks:
            self.check_id_allowlist = runner_filter.checks

    @abstractmethod
    def extract_entity_details(self, entity: Dict[str, Any]) -> Tuple[str, str, Dict[str, Any]]:
        raise NotImplementedError()

    def scan(
        self,
        scanned_file: str,
        entity: Dict[str, Any],
        skipped_checks: List[_SkippedCheck],
        runner_filter: RunnerFilter,
        report_type: Optional[str] = None  # allow runners like TF plan to override the type while using the same registry
    ) -> Dict[BaseCheck, _CheckResult]:

        (entity_type, entity_name, entity_configuration) = self.extract_entity_details(entity)

        results: Dict[BaseCheck, _CheckResult] = {}

        if not isinstance(entity_configuration, dict):
            return results

        checks = self.get_checks(entity_type)
        for check in checks:
            skip_info: _SkippedCheck = {}
            if skipped_checks:
                if check.id in [x["id"] for x in skipped_checks]:
                    skip_info = [x for x in skipped_checks if x["id"] == check.id][0]

            if runner_filter.should_run_check(
                    check,
                    report_type=report_type or self.report_type,
                    file_origin_paths=[scanned_file]
            ):
                result = self.run_check(check, entity_configuration, entity_name, entity_type, scanned_file, skip_info)
                results[check] = result
        return results

    def run_check(
        self,
        check: BaseCheck,
        entity_configuration: Dict[str, List[Any]],
        entity_name: str,
        entity_type: str,
        scanned_file: str,
        skip_info: _SkippedCheck,
    ) -> _CheckResult:
        self.logger.debug("Running check: {} on file {}".format(check.name, scanned_file))
        try:
            result = check.run(
                scanned_file=scanned_file,
                entity_configuration=entity_configuration,
                entity_name=entity_name,
                entity_type=entity_type,
                skip_info=skip_info,
            )
            return result
        except Exception:
            return _CheckResult(
                result=CheckResult.UNKNOWN, suppress_comment="", evaluated_keys=[],
                results_configuration=entity_configuration, check=check, entity=entity_configuration
            )

    @staticmethod
    def _directory_has_init_py(directory: str) -> bool:
        """ Check if a given directory contains a file named __init__.py.

        __init__.py is needed to ensure the directory is a Python module, thus
        can be imported.
        """
        return os.path.exists(os.path.join(directory, "__init__.py"))

    @staticmethod
    def _file_can_be_imported(entry: "os.DirEntry[str]") -> bool:
        """ Verify if a directory entry is a non-magic Python file."""
        return entry.is_file() and not entry.name.startswith("__") and entry.name.endswith(".py")

    def load_external_checks(self, directory: str) -> None:
        """ Browse a directory looking for .py files to import.

        Log an error when the directory does not contains an __init__.py or
        when a .py file has syntax error
        """
        directory = os.path.expanduser(directory)
        self.logger.debug(f"Loading external checks from {directory}")
        for root, _, _ in os.walk(directory):
            sys.path.insert(1, root)
            with os.scandir(root) as directory_content:
                if not self._directory_has_init_py(root):
                    self.logger.info(f"No __init__.py found in {root}. Cannot load any check here.")
                else:
                    for entry in directory_content:
                        if self._file_can_be_imported(entry):
                            check_name = entry.name.replace(".py", "")
                            check_full_path = entry.path

                            # Filter is set while loading external checks so the filter can be informed
                            # of the checks, which need to be handled specially.
                            try:
                                BaseCheckRegistry.__loading_external_checks = True
                                self.logger.debug(f"Importing external check '{check_name}'")

                                spec = importlib.util.spec_from_file_location(check_name, check_full_path)
                                if spec:
                                    module = importlib.util.module_from_spec(spec)
                                    sys.modules[check_name] = module
                                    spec.loader.exec_module(module)  # type: ignore[union-attr] # loader can't be None here
                                else:
                                    self.logger.error(f"Cannot load external check '{check_name}' from {check_full_path}")
                            except Exception:
                                self.logger.error(f"Cannot load external check '{check_name}' from {check_full_path}", exc_info=True)
                            finally:
                                BaseCheckRegistry.__loading_external_checks = False

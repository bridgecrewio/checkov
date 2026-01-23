from __future__ import annotations
import concurrent.futures
import logging
from typing import Any, TYPE_CHECKING

from checkov.common.graph.checks_infra import debug
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.models.enums import CheckResult
from checkov.runner_filter import RunnerFilter

if TYPE_CHECKING:
    from checkov.common.graph.checks_infra.base_check import BaseGraphCheck
    from checkov.common.graph.checks_infra.base_parser import BaseGraphCheckParser
    from checkov.common.typing import _CheckResult, LibraryGraph


class BaseRegistry:
    def __init__(self, parser: BaseGraphCheckParser) -> None:
        self.checks: "list[BaseGraphCheck]" = []
        self.parser = parser

    def load_checks(self) -> None:
        raise NotImplementedError

    def run_checks(
        self, graph_connector: LibraryGraph, runner_filter: RunnerFilter, report_type: str
    ) -> dict[BaseGraphCheck, list[_CheckResult]]:

        check_results: "dict[BaseGraphCheck, list[_CheckResult]]" = {}

        checks_to_run = [c for c in self.checks if runner_filter.should_run_check(c, report_type=report_type)]
        with concurrent.futures.ThreadPoolExecutor() as executor:
            concurrent.futures.wait(
                [executor.submit(self.run_check_parallel, check, check_results, graph_connector)
                 for check in checks_to_run]
            )
        return check_results

    def run_check_parallel(
            self, check: BaseGraphCheck, check_results: dict[BaseGraphCheck, list[_CheckResult]],
            graph_connector: LibraryGraph
    ) -> None:
        logging.debug(f'Running graph check: {check.id}')
        debug.graph_check(check_id=check.id, check_name=check.name)

        passed, failed, unknown = check.run(graph_connector)

        # Apply evaluation_mode aggregation
        if getattr(check, 'evaluation_mode', 'all') == 'any':
            passed, failed, unknown = self._apply_any_mode(passed, failed, unknown)

        evaluated_keys = check.get_evaluated_keys()
        check_result = self._process_check_result(passed, [], CheckResult.PASSED, evaluated_keys)
        check_result = self._process_check_result(failed, check_result, CheckResult.FAILED, evaluated_keys)
        check_result = self._process_check_result(unknown, check_result, CheckResult.UNKNOWN, evaluated_keys)
        check_results[check] = check_result

    @staticmethod
    def _apply_any_mode(
        passed: list[dict[str, Any]],
        failed: list[dict[str, Any]],
        unknown: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
        """Apply 'any' evaluation mode: if at least one resource in a file passes,
        all resources of that type in the same file pass.

        This enables checks like "at least one RUN instruction must contain X".
        """
        if not passed:
            # No resource passed - report one representative failure per file
            seen_files: set[str | None] = set()
            representative: list[dict[str, Any]] = []
            for f in failed:
                fp = f.get(CustomAttributes.FILE_PATH)
                if fp not in seen_files:
                    seen_files.add(fp)
                    representative.append(f)
            return [], representative, unknown

        # At least one resource passed - move failed items in passing files to passed
        passed_files = {v.get(CustomAttributes.FILE_PATH) for v in passed}
        new_failed = [f for f in failed if f.get(CustomAttributes.FILE_PATH) not in passed_files]
        new_passed = passed + [f for f in failed if f.get(CustomAttributes.FILE_PATH) in passed_files]
        new_unknown = [u for u in unknown if u.get(CustomAttributes.FILE_PATH) not in passed_files]
        return new_passed, new_failed, new_unknown

    @staticmethod
    def _process_check_result(
        results: list[dict[str, Any]],
        processed_results: list[_CheckResult],
        result: CheckResult,
        evaluated_keys: list[str],
    ) -> list[_CheckResult]:
        for vertex in results:
            processed_results.append({"result": result, "entity": vertex, "evaluated_keys": evaluated_keys})
        return processed_results

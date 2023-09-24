from __future__ import annotations
import logging
from typing import Any, TYPE_CHECKING

from checkov.common.graph.checks_infra import debug
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
        return {
            check: self.run_check(check=check, graph_connector=graph_connector)
            for check in (c for c in self.checks if runner_filter.should_run_check(c, report_type=report_type))
        }

    def run_check(self, check: BaseGraphCheck, graph_connector: LibraryGraph) -> list[_CheckResult]:
        logging.debug(f'Running graph check: {check.id}')
        debug.graph_check(check_id=check.id, check_name=check.name)

        passed, failed, unknown = check.run(graph_connector)
        evaluated_keys = check.get_evaluated_keys()
        check_result = self._process_check_result(passed, [], CheckResult.PASSED, evaluated_keys)
        check_result = self._process_check_result(failed, check_result, CheckResult.FAILED, evaluated_keys)
        check_result = self._process_check_result(unknown, check_result, CheckResult.UNKNOWN, evaluated_keys)
        return check_result

    @staticmethod
    def _process_check_result(
        results: list[dict[str, Any]],
        processed_results: list[_CheckResult],
        result: CheckResult,
        evaluated_keys: list[str],
    ) -> list[_CheckResult]:
        processed_results.extend(
            {"result": result, "entity": vertex, "evaluated_keys": evaluated_keys}
            for vertex in results
        )
        return processed_results

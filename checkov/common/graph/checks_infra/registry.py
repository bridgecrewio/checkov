from __future__ import annotations

import concurrent.futures
import logging

from typing import List, Dict, Any, TYPE_CHECKING

from checkov.common.models.enums import CheckResult
from checkov.runner_filter import RunnerFilter

if TYPE_CHECKING:
    from networkx import DiGraph
    from checkov.common.graph.checks_infra.base_check import BaseGraphCheck
    from checkov.common.graph.checks_infra.base_parser import BaseGraphCheckParser


class BaseRegistry:
    def __init__(self, parser: BaseGraphCheckParser) -> None:
        self.checks: List[BaseGraphCheck] = []
        self.parser = parser

    def load_checks(self) -> None:
        raise NotImplementedError

    def run_checks(
        self, graph_connector: DiGraph, runner_filter: RunnerFilter, report_type: str
    ) -> Dict[BaseGraphCheck, List[Dict[str, Any]]]:

        check_results: Dict[BaseGraphCheck, List[Dict[str, Any]]] = {}
        checks_to_run = [c for c in self.checks if runner_filter.should_run_check(c, report_type=report_type)]

        with concurrent.futures.ThreadPoolExecutor() as executor:
            concurrent.futures.wait(
                [executor.submit(self.run_check_parallel, check, check_results, graph_connector)
                 for check in checks_to_run]
            )
        return check_results

    def run_check_parallel(
        self, check: BaseGraphCheck, check_results: Dict[BaseGraphCheck, List[Dict[str, Any]]], graph_connector: DiGraph
    ) -> None:
        logging.debug(f'Running graph check: {check.id}')
        passed, failed, unknown = check.run(graph_connector)
        evaluated_keys = check.get_evaluated_keys()
        check_result = self._process_check_result(passed, [], CheckResult.PASSED, evaluated_keys)
        check_result = self._process_check_result(failed, check_result, CheckResult.FAILED, evaluated_keys)
        check_result = self._process_check_result(unknown, check_result, CheckResult.UNKNOWN, evaluated_keys)
        check_results[check] = check_result

    @staticmethod
    def _process_check_result(
        results: List[Dict[str, Any]],
        processed_results: List[Dict[str, Any]],
        result: CheckResult, evaluated_keys: List[str],
    ) -> List[Dict[str, Any]]:
        for vertex in results:
            processed_results.append({"result": result, "entity": vertex, "evaluated_keys": evaluated_keys})
        return processed_results

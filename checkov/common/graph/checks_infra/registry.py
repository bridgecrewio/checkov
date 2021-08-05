import logging
from typing import List, Dict, Any

from networkx import DiGraph

from checkov.common.graph.checks_infra.base_check import BaseGraphCheck
from checkov.common.graph.checks_infra.base_parser import BaseGraphCheckParser
from checkov.common.models.enums import CheckResult
from checkov.runner_filter import RunnerFilter


class BaseRegistry:
    def __init__(self, parser: BaseGraphCheckParser) -> None:
        self.checks: List[BaseGraphCheck] = []
        self.parser = parser

    def load_checks(self):
        raise NotImplementedError

    def run_checks(
        self, graph_connector: DiGraph, runner_filter: RunnerFilter
    ) -> Dict[BaseGraphCheck, List[Dict[str, Any]]]:
        check_results = {}
        for check in self.checks:
            if not runner_filter.should_run_check(check.id, check.bc_id):
                continue
            logging.debug(f'Running graph check: {check.id}')
            passed, failed = check.run(graph_connector)
            check_result = self._process_check_result(passed, [], CheckResult.PASSED)
            check_result = self._process_check_result(failed, check_result, CheckResult.FAILED)
            check_results[check] = check_result
        return check_results

    @staticmethod
    def _process_check_result(results, processed_results, result):
        for vertex in results:
            processed_results.append({"result": result, "entity": vertex})
        return processed_results

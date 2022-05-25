import concurrent.futures
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

    def load_checks(self) -> None:
        raise NotImplementedError

    def run_checks(
        self, graph_connector: DiGraph, runner_filter: RunnerFilter
    ) -> Dict[BaseGraphCheck, List[Dict[str, Any]]]:
        check_results = {}
        checks_to_run = [c for c in self.checks if runner_filter.should_run_check(c)]
        with concurrent.futures.ThreadPoolExecutor() as executor:
            concurrent.futures.wait(
                [executor.submit(self.run_check_parallel, check, check_results, graph_connector)
                 for check in checks_to_run]
            )
        return check_results

    def run_check_parallel(self, check, check_results, graph_connector):
        logging.debug(f'Running graph check: {check.id}')
        passed, failed = check.run(graph_connector)
        evaluated_keys = check.get_evaluated_keys()
        check_result = self._process_check_result(passed, [], CheckResult.PASSED, evaluated_keys)
        check_result = self._process_check_result(failed, check_result, CheckResult.FAILED, evaluated_keys)
        check_results[check] = check_result

    @staticmethod
    def _process_check_result(results, processed_results, result, evaluated_keys) -> List[Dict[str, Any]]:
        for vertex in results:
            processed_results.append({"result": result, "entity": vertex, "evaluated_keys": evaluated_keys})
        return processed_results

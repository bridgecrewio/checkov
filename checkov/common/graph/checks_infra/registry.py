from checkov.common.models.enums import CheckResult
from checkov.runner_filter import RunnerFilter


class BaseRegistry:
    def __init__(self, parser):
        self.checks = []
        self.parser = parser

    def load_checks(self):
        raise NotImplementedError

    def run_checks(self, graph_connector, runner_filter: RunnerFilter):
        check_results = {}
        for check in self.checks:
            if runner_filter.checks and check.id not in runner_filter.checks \
                    or runner_filter.skip_checks and not runner_filter.should_run_check(check.id):
                continue
            passed, failed = check.run(graph_connector)
            check_result = self._process_check_result(passed, [], CheckResult.PASSED)
            check_result = self._process_check_result(failed, check_result, CheckResult.FAILED)
            check_results[check] = check_result
        return check_results

    @staticmethod
    def _process_check_result(results, processed_results, result):
        for vertex in results:
            processed_results.append({'result': result, 'entity': vertex})
        return processed_results

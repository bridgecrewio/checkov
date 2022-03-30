from checkov.common.output.report import CheckType, Report
from checkov.common.runners.object_runner import Runner as ObjectRunner
from checkov.runner_filter import RunnerFilter


class Runner(ObjectRunner):
    check_type = CheckType.OPENAPI

    def import_registry(self):
        from checkov.openapi.checks.registry import openapi_registry
        return openapi_registry

    def _parse_file(self, f):
        raise Exception("parser should be implemented")

    def get_start_end_lines(self, end, result_config, start):
        raise Exception("get_start_end_lines should be implemented")

    def require_external_checks(self):
        return False

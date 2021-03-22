from checkov.graph.checks.checks_infra.base_check import BaseGraphCheck


class BaseGraphCheckParser:
    def parse_raw_check(self, raw_check, **kwargs) -> BaseGraphCheck:
        raise NotImplementedError

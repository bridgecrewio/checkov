from typing import Dict, Any

from checkov.common.graph.checks_infra.base_check import BaseGraphCheck


class BaseGraphCheckParser:
    def parse_raw_check(self, raw_check: Dict[str, Dict[str, Any]], **kwargs: Any) -> BaseGraphCheck:
        raise NotImplementedError

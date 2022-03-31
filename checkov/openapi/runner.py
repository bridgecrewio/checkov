from typing import List, Dict, Union, Any

from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.common.output.report import CheckType
from checkov.common.runners.object_runner import Runner as ObjectRunner


class Runner(ObjectRunner):
    check_type = CheckType.OPENAPI

    def import_registry(self) -> BaseCheckRegistry:
        from checkov.openapi.checks.registry import openapi_registry
        return openapi_registry

    def _parse_file(self, f: str) -> None:
        raise Exception("parser should be implemented")

    def get_start_end_lines(self, end: int, result_config: Union[List[Dict[str, Any]], List[Dict[str, Any]]], start: int) -> None:
        raise Exception("get_start_end_lines should be implemented")

    def require_external_checks(self) -> bool:
        return False

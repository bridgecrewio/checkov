import logging
from typing import List, Dict, Union, Any, Tuple

from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.common.output.report import CheckType
from checkov.yaml_doc.runner import Runner as YamlRunner
from checkov.json_doc.runner import Runner as JsonRunner

logger = logging.getLogger(__name__)


class Runner(YamlRunner, JsonRunner):
    check_type = CheckType.OPENAPI

    def import_registry(self) -> BaseCheckRegistry:
        from checkov.openapi.checks.registry import openapi_registry
        return openapi_registry

    def _parse_file(self, f: str) -> Tuple[Dict[str, Any], Tuple[int, str]]:
        if f.endswith(".json"):
            return JsonRunner._parse_file(self, f)
        elif f.endswith(".yml") or f.endswith(".yaml"):
            return YamlRunner._parse_file(self, f)
        else:
            logger.warn(f'file {f} is not a json nor yaml.')

    def get_start_end_lines(self, end: int, result_config: Union[List[Dict[str, Any]], List[Dict[str, Any]]],
                            start: int) -> Tuple[int, int]:
        if hasattr(result_config, "start_mark"):
            return JsonRunner.get_start_end_lines(self, end, result_config, start)
        elif '__startline__' in result_config:
            return YamlRunner.get_start_end_lines(self, end, result_config, start)

    def require_external_checks(self) -> bool:
        return False

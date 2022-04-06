from __future__ import annotations

import logging
import os
from typing import Any

from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.common.output.report import CheckType, Report
from checkov.runner_filter import RunnerFilter
from checkov.yaml_doc.runner import Runner as YamlRunner
from checkov.json_doc.runner import Runner as JsonRunner

logger = logging.getLogger(__name__)


class Runner(YamlRunner, JsonRunner):
    check_type = CheckType.OPENAPI

    def import_registry(self) -> BaseCheckRegistry:
        from checkov.openapi.checks.registry import openapi_registry
        return openapi_registry

    def _parse_file(self, f: str) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | tuple[None, None]:
        if f.endswith(".json"):
            parsed_json = JsonRunner._parse_file(self, f)
            if self.is_valid(parsed_json[0]):
                return parsed_json  # type:ignore[no-any-return]
        elif f.endswith(".yml") or f.endswith(".yaml"):
            parsed_yaml = YamlRunner._parse_file(self, f)
            if self.is_valid(parsed_yaml[0]):
                return parsed_yaml  # type:ignore[no-any-return]

        return None, None

    def get_start_end_lines(self, end: int, result_config: dict[str, Any], start: int) -> tuple[int, int]:
        if hasattr(result_config, "start_mark"):
            return JsonRunner.get_start_end_lines(self, end, result_config, start)  # type:ignore[no-any-return]
        elif '__startline__' in result_config:
            return YamlRunner.get_start_end_lines(self, end, result_config, start)  # type:ignore[no-any-return]

        raise Exception("Unexpected dictionary format.")

    def require_external_checks(self) -> bool:
        return False

    def is_valid(self, conf: dict[str, Any]) -> bool:
        """validate openAPI configuration."""
        # 'swagger' is a required element on v2.0, and 'openapi' is required on v3.
        return bool(conf and ('swagger' in conf or 'openapi' in conf))

    def get_resource(self, file_path: str, key: str) -> str:
        return f'{key}'

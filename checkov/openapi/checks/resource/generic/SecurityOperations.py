from __future__ import annotations

from typing import Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.checks.enums import BlockType
from checkov.openapi.checks.base_openapi_check import BaseOpenapiCheck


class SecurityOperations(BaseOpenapiCheck):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_5"
        name = "Ensure that security operations is not empty."
        categories = [CheckCategories.API_SECURITY]
        supported_resources = ['security']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_resources,
                         block_type=BlockType.DOCUMENT)

    def scan_entity_conf(self, conf: dict[str, Any], entity_type: str) -> tuple[CheckResult, dict[str, Any]]:  # type:ignore[override]  # return type is different than the base class
        self.evaluated_keys = ['security', 'paths']

        # Check if security field is present and not empty at the root level
        root_security = conf.get('security')
        if root_security:
            return CheckResult.PASSED, conf

         # If security field is not present or empty at the root level, check within each operation
        paths = conf.get('paths', {}) or {}
        if isinstance(paths, dict):
            for path, http_method in paths.items():
                if self.is_start_end_line(path):
                    continue
                if isinstance(http_method, dict):
                    for op_name, op_val in http_method.items():
                        if self.is_start_end_line(op_name):
                            continue
                        self.evaluated_keys = ['security']
                        if not isinstance(op_val, dict):
                            continue
                        if 'security' not in op_val:
                            return CheckResult.FAILED, conf

                        security = op_val['security']
                        if not security:
                            return CheckResult.FAILED, paths

        return CheckResult.PASSED, conf


check = SecurityOperations()

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
        self.evaluated_keys = ['paths']

        paths = conf.get('paths', {})
        for path, http_method in paths.items():
            if self.is_start_end_line(path):
                continue
            for op_name, op_val in http_method.items():
                if self.is_start_end_line(op_name):
                    continue
                self.evaluated_keys = ['security']
                if 'security' not in op_val:
                    return CheckResult.FAILED, conf

                security = op_val['security']
                if not security:
                    return CheckResult.FAILED, paths

        return CheckResult.PASSED, conf


check = SecurityOperations()

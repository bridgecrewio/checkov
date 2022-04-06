from __future__ import annotations

from typing import Dict, Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.checks.enums import BlockType
from checkov.openapi.checks.base_openapi_check import BaseOpenapiCheck


class SecurityOperations(BaseOpenapiCheck):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_5"
        name = "Ensure that security operations is not empty."
        categories = [CheckCategories.NETWORKING]
        supported_resources = ['security']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_resources,
                         block_type=BlockType.DOCUMENT)

    def scan_entity_conf(self, conf: Dict[str, Any]) -> tuple[CheckResult, dict[str, Any] | None]:
        self.evaluated_keys = ['paths']
        for path, http_method in conf['paths'].items():
            for op_name, op_val in http_method.items():
                self.evaluated_keys = ['security']
                if 'security' not in op_val:
                    return CheckResult.FAILED, conf

                security = op_val['security']
                if not security: #  TODO when [] parser didnt add lines
                    return CheckResult.FAILED, security

        return CheckResult.PASSED, conf




check = SecurityOperations()

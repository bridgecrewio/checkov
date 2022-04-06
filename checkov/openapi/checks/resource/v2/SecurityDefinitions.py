from __future__ import annotations

from typing import Dict, Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.checks.enums import BlockType
from checkov.openapi.checks.base_openapi_check import BaseOpenapiCheck


class SecurityDefinitions(BaseOpenapiCheck):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_1"
        name = "Ensure that securityDefinitions is defined and not empty."
        categories = [CheckCategories.NETWORKING]
        supported_resources = ['securityDefinitions']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_resources,
                         block_type=BlockType.DOCUMENT)

    def scan_entity_conf(self, conf: Dict[str, Any]) -> tuple[CheckResult, dict[str, Any] | None]:
        self.evaluated_keys = ["securityDefinitions"]
        if "securityDefinitions" not in conf:
            return CheckResult.FAILED, conf

        content = conf["securityDefinitions"]
        if not content or ('__startline__' in content and len(content) <= 2):
            return CheckResult.FAILED, content
        return CheckResult.PASSED, content

check = SecurityDefinitions()

from __future__ import annotations

from typing import Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.checks.enums import BlockType
from checkov.common.parsers.node import DictNode
from checkov.openapi.checks.base_openapi_check import BaseOpenapiCheck


class SecurityDefinitions(BaseOpenapiCheck):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_1"
        name = "Ensure that securityDefinitions is defined and not empty."
        categories = [CheckCategories.API_SECURITY]
        supported_resources = ['securityDefinitions']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_resources,
                         block_type=BlockType.DOCUMENT)

    def scan_entity_conf(self, conf: dict[str, Any]) -> tuple[CheckResult, dict[str, Any] | None]:
        self.evaluated_keys = ["securityDefinitions"]
        if "securityDefinitions" not in conf:
            return CheckResult.FAILED, conf

        security_definitions = conf["securityDefinitions"]
        if not security_definitions or (not isinstance(security_definitions, DictNode) and len(security_definitions) <= 2):
            return CheckResult.FAILED, security_definitions
        return CheckResult.PASSED, security_definitions

check = SecurityDefinitions()

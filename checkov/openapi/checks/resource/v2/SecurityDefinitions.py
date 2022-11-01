from __future__ import annotations

from typing import Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.checks.enums import BlockType
from checkov.common.parsers.node import DictNode
from checkov.openapi.checks.resource.v2.BaseOpenapiCheckV2 import BaseOpenapiCheckV2


class SecurityDefinitions(BaseOpenapiCheckV2):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_1"
        name = "Ensure that securityDefinitions is defined and not empty - version 2.0 files"
        categories = (CheckCategories.API_SECURITY,)
        supported_resources = ('securityDefinitions',)
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_resources,
                         block_type=BlockType.DOCUMENT)

    def scan_openapi_conf(self, conf: dict[str, Any], entity_type: str) -> tuple[CheckResult, dict[str, Any]]:
        self.evaluated_keys = ["securityDefinitions"]
        if "securityDefinitions" not in conf:
            return CheckResult.FAILED, conf

        security_definitions = conf["securityDefinitions"]
        if not security_definitions or (not isinstance(security_definitions, DictNode) and len(security_definitions) <= 2):
            return CheckResult.FAILED, security_definitions
        return CheckResult.PASSED, security_definitions


check = SecurityDefinitions()

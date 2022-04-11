from typing import Dict, Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.checks.enums import BlockType
from checkov.openapi.checks.base_openapi_check import BaseOpenapiCheck


class GlobalSecurityFieldIsEmpty(BaseOpenapiCheck):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_4"
        name = "Ensure that the security field has rules defined"
        categories = [CheckCategories.API_SECURITY]
        supported_resources = ['security']
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_resources,
                         block_type=BlockType.DOCUMENT)

    def scan_entity_conf(self, conf: Dict[str, Any], entity_type: str) -> CheckResult:
        security_rules = conf.get("security")

        if security_rules:
            return CheckResult.PASSED
        return CheckResult.FAILED


check = GlobalSecurityFieldIsEmpty()

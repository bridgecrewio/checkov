from typing import Dict, Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.checks.enums import BlockType
from checkov.openapi.checks.base_openapi_check import BaseOpenapiCheck


class SecurityDefinitionsV2(BaseOpenapiCheck):
    def __init__(self) -> None:
        id = "CKV_OPENAPI_1"
        name = "Ensure that securityDefinitions has defined."
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_entities=["*"],
                         block_type=BlockType.DOCUMENT)

    def scan_entity_conf(self, conf: Dict[str, Any], entity_type: str) -> CheckResult:
        self.evaluated_container_keys = ["securityDefinitions"]

        if "securityDefinitions" not in conf or not conf["securityDefinitions"]:
            return CheckResult.FAILED

        return CheckResult.PASSED


check = SecurityDefinitionsV2()

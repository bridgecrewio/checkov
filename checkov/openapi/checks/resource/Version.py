from typing import Dict, Any
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.json_doc.enums import BlockType
from checkov.openapi.checks.base_openapi_check import BaseOpenapiCheck


class Version(BaseOpenapiCheck):
    def __init__(self) -> None:
        id = "CKV_OAPI_1"
        name = "Ensure that the --kubelet-https argument is set to true"
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_entities=["*"], block_type=BlockType.DOCUMENT)

    def scan_entity_conf(self, conf: Dict[str, Any], entity_type: str) -> CheckResult:
        self.evaluated_container_keys = ["info"]
        version = conf["info"]["version"]
        if "1" not in version:
            return CheckResult.FAILED

        return CheckResult.PASSED


check = Version()

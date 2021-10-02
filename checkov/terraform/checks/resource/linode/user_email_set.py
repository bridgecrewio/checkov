from typing import Dict, List, Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class EmailExists(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure email is set"
        id = "CKV_LIN_3"
        supported_resources = ["linode_user"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        if conf.get("email"):
            return CheckResult.PASSED
        return CheckResult.FAILED


check = EmailExists()

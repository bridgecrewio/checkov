from typing import Dict, List, Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class AuthorizedKeys(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure SSH key set in authorized_keys"
        id = "CKV_LIN_2"
        supported_resources = ["linode_instance"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        if conf.get("authorized_keys"):
            return CheckResult.PASSED
        return CheckResult.FAILED


check = AuthorizedKeys()

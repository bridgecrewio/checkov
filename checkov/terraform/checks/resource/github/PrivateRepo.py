from typing import Dict, List, Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class PrivateRepo(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Repository is Private"
        id = "CKV_GIT_1"
        supported_resources = ["github_repository"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        if conf.get("private") == [True]:
            return CheckResult.PASSED
        elif conf.get("visibility") in [["private"], ["internal"]]:
            return CheckResult.PASSED
        return CheckResult.FAILED


check = PrivateRepo()

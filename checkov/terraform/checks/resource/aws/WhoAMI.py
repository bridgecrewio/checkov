from typing import Dict, Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class WhoAMI(BaseResourceCheck):
    def __init__(self) -> None:
        name = "WhoAMI vulnerability: cloud image name confusion attack"
        id = "CKV_AWS_386"
        supported_resources = ['aws_ami']
        categories = [CheckCategories.SUPPLY_CHAIN]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        if "image_owner_alias" in conf or 'owner_id' in conf:
            return CheckResult.PASSED
        if 'name' in conf:
            if '*' in conf['name'][0]:
                return CheckResult.FAILED
        return CheckResult.PASSED


check = WhoAMI()

from typing import Dict, List, Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class VMDiskWithPublicAccess(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Azure Virtual Machine disks are configured without public network access"
        id = "CKV_AZURE_251"
        supported_resources = ['azurerm_managed_disk']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        if "public_network_access_enabled" in conf:
            if "True" in conf["public_network_access_enabled"] or True in conf["public_network_access_enabled"]:
                return CheckResult.FAILED
            else:
                return CheckResult.PASSED
        else:
            return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ['public_network_access_enabled']


check = VMDiskWithPublicAccess()

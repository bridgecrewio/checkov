from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_check import BaseResourceCheck
from typing import List, Dict, Any


class AzureDefenderOnSqlServersVMS(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that Azure Defender is set to On for SQL servers on machines"
        id = "CKV_AZURE_79"
        supported_resources = ("Microsoft.Cache/Redis",)
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        properties = conf.get("properties", {})
        resourceType = properties.get("resourceType")
        tier = properties.get("tier")
        if resourceType != "SqlServerVirtualMachines" or tier == "Standard":
            return CheckResult.FAILED
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ["resource_type", "tier"]


check = AzureDefenderOnSqlServersVMS()

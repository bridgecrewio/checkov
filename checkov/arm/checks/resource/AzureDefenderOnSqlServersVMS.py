from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_check import BaseResourceCheck
from typing import List, Dict, Any


class AzureDefenderOnSqlServersVMS(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that Azure Defender is set to On for SQL servers on machines"
        id = "CKV_AZURE_79"
        supported_resources = ("Microsoft.Security/pricing",)
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        resource_type = conf.get("resource_type")
        if resource_type == "Microsoft.Security/pricing":
            tier = conf.get("tier")
            if tier == "SqlServerVirtualMachines":
                return CheckResult.PASSED
            else:
                return CheckResult.FAILED
        return CheckResult.UNKNOWN


def get_evaluated_keys(self) -> List[str]:
        return ["resource_type", "tier"]


check = AzureDefenderOnSqlServersVMS()

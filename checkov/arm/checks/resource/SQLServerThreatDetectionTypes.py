from typing import Dict, Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck


# https://docs.microsoft.com/en-us/azure/templates/microsoft.sql/2019-06-01-preview/servers
# https://docs.microsoft.com/en-us/azure/templates/microsoft.sql/2017-03-01-preview/servers/securityalertpolicies


class SQLServerThreatDetectionTypes(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that 'Threat Detection types' is set to 'All'"
        id = "CKV_AZURE_25"
        supported_resources = ("Microsoft.Sql/servers/databases",)  # 'Microsoft.Sql/servers'
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        resources = conf.get("resources")
        if isinstance(resources, list):
            for resource in resources:
                if "type" in resource:
                    if resource["type"] in (
                        "Microsoft.Sql/servers/databases/securityAlertPolicies",
                        "securityAlertPolicies",
                    ):
                        properties = resource.get("properties")
                        if isinstance(properties, dict):
                            if "state" in properties and properties["state"].lower() == "enabled":
                                if not properties.get("disabledAlerts"):
                                    return CheckResult.PASSED

        return CheckResult.FAILED


check = SQLServerThreatDetectionTypes()

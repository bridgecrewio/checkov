from typing import Dict, Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_check import BaseResourceCheck


class AzureMLWorkspacePrivateEndpoint(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Azure Machine learning workspace is not configured with private endpoint"
        id = "CKV_AZURE_239"
        supported_resources = ["Microsoft.MachineLearningServices/workspaces"]
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        properties = conf.get("properties")
        if isinstance(properties, dict):
            managed_network = properties.get("managedNetwork")
            if isinstance(managed_network, dict):
                ob_rules = managed_network.get("outboundRules")
                if isinstance(ob_rules, dict):
                    # check no outbound rule has private endpoint type
                    for rule in ob_rules.values():
                        if rule.get("type") == "PrivateEndpoint":
                            return CheckResult.FAILED
        return CheckResult.PASSED


check = AzureMLWorkspacePrivateEndpoint()

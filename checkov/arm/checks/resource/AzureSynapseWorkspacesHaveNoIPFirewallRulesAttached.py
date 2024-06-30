from typing import Dict, List, Any
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_check import BaseResourceCheck


class AzureSynapseWorkspacesHaveNoIPFirewallRulesAttached(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure Synapse workspaces have no IP firewall rules attached"
        id = "CKV2_AZURE_19"
        supported_resources = ["Microsoft.Synapse/workspaces"]
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        depends_on = conf.get("dependsOn")
        if depends_on is None or not len(depends_on):
            return CheckResult.PASSED
        if any('Microsoft.Synapse/workspaces/firewallRules' in item for item in depends_on):
            return CheckResult.FAILED
        return CheckResult.PASSED


check = AzureSynapseWorkspacesHaveNoIPFirewallRulesAttached()

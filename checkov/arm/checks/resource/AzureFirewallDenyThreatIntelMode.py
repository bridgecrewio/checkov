from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class AzureFirewallDenyThreatIntelMode(BaseResourceValueCheck):
    def __init__(self) -> None:
        """
        https://azure.github.io/PSRule.Rules.Azure/en/rules/Azure.Firewall.Mode/
        Configure deny on threat intel for classic managed Azure Firewalls
        """
        name = "Ensure DenyIntelMode is set to Deny for Azure Firewalls"
        id = "CKV_AZURE_216"
        supported_resources = ("Microsoft.Network/azureFirewalls",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'properties/threatIntelMode'

    def get_expected_value(self) -> Any:
        return "Deny"


check = AzureFirewallDenyThreatIntelMode()

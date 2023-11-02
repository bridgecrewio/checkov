from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class KeyVaultEnablesFirewallRulesSettings(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that key vault allows firewall rules settings"
        id = "CKV_AZURE_109"
        supported_resources = ("Microsoft.KeyVault/vaults",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/networkAcls/defaultAction"

    def get_expected_value(self) -> Any:
        return "Deny"


check = KeyVaultEnablesFirewallRulesSettings()

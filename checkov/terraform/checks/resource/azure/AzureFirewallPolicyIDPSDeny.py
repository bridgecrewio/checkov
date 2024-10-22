
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AzureFirewallPolicyIDPSDeny(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Firewall policy has IDPS mode as deny"
        id = "CKV_AZURE_220"
        supported_resources = ['azurerm_firewall_policy']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "intrusion_detection/[0]/mode"

    def get_expected_value(self) -> str:
        return "Deny"


check = AzureFirewallPolicyIDPSDeny()

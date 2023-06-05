from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from typing import Any


class AzureFirewallDefinesPolicy(BaseResourceValueCheck) :
    def __init__(self) -> None:
        name = "Ensure Firewall defines a firewall policy"
        id = "CKV_AZURE_219"
        supported_resources = ['azurerm_firewall']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "firewall_policy_id"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = AzureFirewallDefinesPolicy()

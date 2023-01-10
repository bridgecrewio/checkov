from typing import Any

from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AzureServicebusHasCMK(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure Service Bus uses a customer-managed key to encrypt data"
        id = "CKV_AZURE_201"
        supported_resources = ("azurerm_servicebus_namespace",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "customer_managed_key/[0]/key_vault_key_id"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = AzureServicebusHasCMK()

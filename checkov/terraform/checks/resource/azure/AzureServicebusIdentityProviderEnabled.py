from typing import Any

from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AzureServicebusIdentityProviderEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Managed identity provider is enabled for Azure Service Bus"
        id = "CKV_AZURE_202"
        supported_resources = ("azurerm_servicebus_namespace",)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "identity/[0]/type"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = AzureServicebusIdentityProviderEnabled()

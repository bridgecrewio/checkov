from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AzureServicebusDoubleEncryptionEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure Service Bus uses double encryption"
        id = "CKV_AZURE_199"
        supported_resources = ("azurerm_servicebus_namespace",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "customer_managed_key/[0]/infrastructure_encryption_enabled"

    def get_expected_value(self) -> Any:
        return True


check = AzureServicebusDoubleEncryptionEnabled()

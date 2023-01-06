from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AzureServicebusMinTLSVersion(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Azure Service Bus is using the latest version of TLS encryption"
        id = "CKV_AZURE_205"
        supported_resources = ("azurerm_servicebus_namespace",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "minimum_tls_version"

    def get_expected_value(self) -> Any:
        return "1.2"


check = AzureServicebusMinTLSVersion()

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class ACRPublicNetworkAccessDisabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure ACR set to disable public networking"
        id = "CKV_AZURE_139"
        supported_resources = ['azurerm_container_registry']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "public_network_access_enabled"

    def get_expected_value(self):
        return False


check = ACRPublicNetworkAccessDisabled()

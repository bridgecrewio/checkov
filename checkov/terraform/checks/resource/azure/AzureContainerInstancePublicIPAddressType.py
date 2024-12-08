from typing import List

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AzureContainerInstancePublicIPAddressType(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure Container group is deployed into virtual network"
        id = "CKV_AZURE_245"
        supported_resources = ('azurerm_container_group',)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'ip_address_type'

    def get_expected_values(self) -> List[str]:
        return ['Private', 'None']


check = AzureContainerInstancePublicIPAddressType()

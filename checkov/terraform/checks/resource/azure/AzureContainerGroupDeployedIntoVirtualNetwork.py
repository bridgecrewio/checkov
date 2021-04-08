from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AzureContainerGroupDeployedIntoVirtualNetwork(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that Azure Container group is deployed into virtual network"
        id = "CKV_AZURE_98"
        supported_resources = ['azurerm_container_group']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'network_profile_id'

    def get_expected_value(self):
        return ANY_VALUE


check = AzureContainerGroupDeployedIntoVirtualNetwork()

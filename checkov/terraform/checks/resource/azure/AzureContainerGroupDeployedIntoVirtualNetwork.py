from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AzureContainerGroupDeployedIntoVirtualNetwork(BaseResourceValueCheck):
    def __init__(self):
        # From Azure:
        # network_profile_id is deprecated by Azure. For users who want to continue to manage existing
        # azurerm_container_group that rely on network_profile_id, please stay on provider versions prior
        # to v3.16.0. Otherwise, use subnet_ids instead.
        name = "Ensure that Azure Container group is deployed into virtual network"
        id = "CKV_AZURE_98"
        supported_resources = ['azurerm_container_group']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'subnet_ids'

    def get_expected_value(self):
        return ANY_VALUE


check = AzureContainerGroupDeployedIntoVirtualNetwork()

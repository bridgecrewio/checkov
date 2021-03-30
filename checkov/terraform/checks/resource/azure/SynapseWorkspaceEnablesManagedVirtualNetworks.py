from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class SynapseWorkspaceEnablesManagedVirtualNetworks(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that Azure Synapse workspaces enables managed virtual networks"
        id = "CKV_AZURE_58"
        supported_resources = ['azurerm_synapse_workspace']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'managed_virtual_network_enabled'


check = SynapseWorkspaceEnablesManagedVirtualNetworks()

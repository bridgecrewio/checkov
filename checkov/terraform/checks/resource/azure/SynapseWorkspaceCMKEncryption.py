from checkov.common.models.consts import ANY_VALUE
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class SynapseWorkspaceCMKEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Azure Synapse Workspace is encrypted with a CMK"
        id = "CKV_AZURE_240"
        supported_resources = ['azurerm_synapse_workspace']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "customer_managed_key/[0]/key_name"

    def get_expected_value(self):
        return ANY_VALUE


check = SynapseWorkspaceCMKEncryption()

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AKSUsesAzurePoliciesAddon(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that AKS uses Azure Policies Add-on"
        id = "CKV_AZURE_116"
        supported_resources = ['azurerm_kubernetes_cluster']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "addon_profile/[0]/azure_policy/[0]/enabled"


check = AKSUsesAzurePoliciesAddon()

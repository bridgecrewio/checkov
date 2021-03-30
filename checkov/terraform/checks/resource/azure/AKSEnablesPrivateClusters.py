from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class APIServicesUseVirtualNetwork(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that AKS enables private clusters"
        id = "CKV_AZURE_115"
        supported_resources = ['azurerm_kubernetes_cluster']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "private_cluster_enabled"


check = APIServicesUseVirtualNetwork()

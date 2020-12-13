from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AKSRbacEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure RBAC is enabled on AKS clusters"
        id = "CKV_AZURE_5"
        supported_resources = ['azurerm_kubernetes_cluster']
        categories = [CheckCategories.KUBERNETES]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'role_based_access_control/[0]/enabled'


check = AKSRbacEnabled()

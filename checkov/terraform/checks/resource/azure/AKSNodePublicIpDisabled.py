from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from typing import List, Any


class AKSNodePublicIpDisabled(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure AKS cluster nodes do not have public IP addresses"
        id = "CKV_AZURE_143"
        supported_resources = ['azurerm_kubernetes_cluster']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "default_node_pool/[0]/enable_node_public_ip"

    def get_forbidden_values(self) -> List[Any]:
        return [True]


check = AKSNodePublicIpDisabled()

from typing import List, Any

from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckCategories


class KubernetesClusterHTTPApplicationRouting(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure Azure AKS cluster HTTP application routing is disabled"
        id = "CKV_AZURE_246"
        supported_resources = ('azurerm_kubernetes_cluster',)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "http_application_routing_enabled"

    def get_forbidden_values(self) -> List[Any]:
        return [True]


check = KubernetesClusterHTTPApplicationRouting()

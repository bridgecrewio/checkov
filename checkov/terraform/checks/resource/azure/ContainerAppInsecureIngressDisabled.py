from typing import List, Any

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class ContainerAppInsecureIngressDisabled(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure Container App does not allow insecure HTTP connections in its ingress"
        id = "CKV_AZURE_253"
        supported_resources = ["azurerm_container_app"]
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "ingress/[0]/allow_insecure_connections"

    def get_forbidden_values(self) -> List[Any]:
        return [True]


check = ContainerAppInsecureIngressDisabled()

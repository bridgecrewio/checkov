from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from typing import List, Any


class AzureSearchAllowedIPsNotGlobal(BaseResourceNegativeValueCheck):
    def __init__(self):
        # Setting the allowed ips to include global routes CIDR - 0.0.0.0/0 makes the resource public
        name = "Ensure Azure search service allowed IPS does not give public Access"
        id = "CKV_AZURE_206"
        supported_resources = ['azurerm_search_service']
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "allowed_ips"

    def get_forbidden_values(self) -> List[Any]:
        return ["0.0.0.0/0"]


check = AzureSearchAllowedIPsNotGlobal()

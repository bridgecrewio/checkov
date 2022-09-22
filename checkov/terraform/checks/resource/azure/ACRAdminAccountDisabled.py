from checkov.common.models.enums import CheckCategories
from typing import List, Any
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class ACRAdminAccountDisabled(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure ACR admin account is disabled"
        id = "CKV_AZURE_137"
        supported_resources = ['azurerm_container_registry']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "admin_enabled"

    def get_forbidden_values(self) -> List[Any]:
        return [True]


check = ACRAdminAccountDisabled()

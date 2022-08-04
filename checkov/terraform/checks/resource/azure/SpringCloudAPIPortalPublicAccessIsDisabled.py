from typing import List, Any
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class SpringCloudAPIPortalPublicAccessIsDisabled(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensures Spring Cloud API Portal Public Access Is Disabled"
        id = "CKV_AZURE_162"
        supported_resources = ['azurerm_spring_cloud_api_portal']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "public_network_access_enabled"

    def get_forbidden_values(self) -> List[Any]:
        return [True]


check = SpringCloudAPIPortalPublicAccessIsDisabled()

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class SpringCloudAPIPortalHTTPSOnly(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensures Spring Cloud API Portal is enabled on for HTTPS"
        id = "CKV_AZURE_161"
        supported_resources = ("azurerm_spring_cloud_api_portal",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "https_only_enabled"


check = SpringCloudAPIPortalHTTPSOnly()

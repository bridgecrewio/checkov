from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class ACRDedicatedDataEndpointEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure dedicated data endpoints are enabled."
        id = "CKV_AZURE_237"
        supported_resources = ("azurerm_container_registry",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "data_endpoint_enabled"


check = ACRDedicatedDataEndpointEnabled()

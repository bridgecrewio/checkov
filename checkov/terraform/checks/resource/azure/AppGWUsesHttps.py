from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AppGWUsesHttps(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Azure Application gateways listener that allow connection requests over HTTP"
        id = "CKV_AZURE_217"
        supported_resources = ("azurerm_application_gateway",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_expected_value(self) -> str:
        return "Https"

    def get_inspected_key(self) -> str:
        return "http_listener/[0]/protocol"


check = AppGWUsesHttps()

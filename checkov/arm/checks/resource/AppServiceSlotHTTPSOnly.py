from checkov.arm.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class AppServiceSlotHTTPSOnly(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure web app redirects all HTTP traffic to HTTPS in Azure App Service Slot"
        id = "CKV_AZURE_153"
        supported_resources = ("Microsoft.Web/sites", "Microsoft.Web/sites/slots",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/httpsOnly"


check = AppServiceSlotHTTPSOnly()

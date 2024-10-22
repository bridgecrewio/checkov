
from checkov.arm.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class AppServiceHttpLoggingEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that App service enables HTTP logging"
        id = "CKV_AZURE_63"
        supported_resources = ["Microsoft.Web/sites/config"]
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/httpLoggingEnabled"

    def get_expected_value(self) -> bool:
        return True


check = AppServiceHttpLoggingEnabled()

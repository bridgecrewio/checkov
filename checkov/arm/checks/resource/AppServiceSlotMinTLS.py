from checkov.arm.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class AppServiceSlotMinTLS(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure the App service slot is using the latest version of TLS encryption"
        id = "CKV_AZURE_154"
        supported_resources = ("Microsoft.Web/sites", "Microsoft.Web/sites/slots")
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self) -> str:
        return "properties/siteConfig/minTlsVersion"

    def get_expected_value(self) -> str:
        return '1.2'


check = AppServiceSlotMinTLS()

from checkov.arm.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class AppServiceSlotDebugDisabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure debugging is disabled for the App service slot"
        id = "CKV_AZURE_155"
        supported_resources = ('Microsoft.Web/sites/slots', 'Microsoft.Web/sites',)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self) -> str:
        return "properties/siteConfig/remoteDebuggingEnabled"

    def get_expected_value(self) -> bool:
        return False


check = AppServiceSlotDebugDisabled()

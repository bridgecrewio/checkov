from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class AppServiceRemoteDebuggingNotEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that remote debugging is not enabled for app services"
        id = "CKV_AZURE_72"
        supported_resources = ["Microsoft.Web/sites",]
        categories = [CheckCategories.GENERAL_SECURITY,]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED,)

    def get_inspected_key(self) -> str:
        return "properties/siteConfig/remoteDebuggingEnabled"

    def get_expected_value(self) -> bool:
        return False


check = AppServiceRemoteDebuggingNotEnabled()

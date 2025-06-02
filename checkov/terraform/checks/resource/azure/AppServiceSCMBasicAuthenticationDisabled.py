from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AppServiceSCMBasicAuthenticationDisabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that basic authentication for SCM is disabled for app services"
        id = "CKV_AZURE_237"
        supported_resources = ('azurerm_linux_web_app', 'azurerm_windows_web_app')
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self) -> str:
        return "webdeploy_publish_basic_authentication_enabled"

    def get_expected_value(self) -> Any:
        return False


check = AppServiceSCMBasicAuthenticationDisabled()

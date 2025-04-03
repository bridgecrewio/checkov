from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AppServiceIPRestrictionDefaultActionDeny(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure the default IP Restriction action is set to 'Deny'"
        id = "CKV_AZURE_239"
        supported_resources = ('azurerm_linux_web_app', 'azurerm_windows_web_app')
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self) -> str:
        return "site_config/[0]/ip_restriction_default_action/[0]"

    def get_expected_value(self) -> Any:
        return "Deny"


check = AppServiceIPRestrictionDefaultActionDeny()

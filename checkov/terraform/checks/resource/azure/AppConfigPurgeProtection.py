
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from typing import Any


class AppConfigPurgeProtection(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure App configuration pruge protection is enabled"
        id = "CKV_AZURE_187"
        supported_resources = ("azurerm_app_configuration",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.FAILED)

    def get_inspected_key(self) -> str:
        return "purge_protection_enabled"

    def get_expected_value(self) -> Any:
        return True


check = AppConfigPurgeProtection()

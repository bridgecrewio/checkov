from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck
from typing import Any


class AppServiceJavaVersion(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that 'Java version' is the latest, if used to run the web app"
        id = "CKV_AZURE_83"
        supported_resources = ('Microsoft.Web/sites',)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.UNKNOWN)

    def get_inspected_key(self) -> Any:
        return "site_config/java_version"

    def get_expected_value(self) -> str:
        return '17'


check = AppServiceJavaVersion()

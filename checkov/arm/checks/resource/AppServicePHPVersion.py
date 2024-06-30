from typing import Any, List
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class AppServicePHPVersion(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that 'PHP version' is the latest, if used to run the web app"
        id = "CKV_AZURE_81"
        supported_resources = ["Microsoft.Web/sites"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.UNKNOWN)

    def get_inspected_key(self) -> str:
        return "properties/siteConfig/phpVersion"

    def get_expected_values(self) -> List[Any]:
        return ["8.1", "8.2"]


check = AppServicePHPVersion()

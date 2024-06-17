from typing import Any, List, Dict
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

    def get_expected_value(self) -> List[Any]:
        return ["8.1", "8.2"]

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        if conf.get("properties") and conf["properties"].get("siteConfig"):
            php_version = conf.get("properties", {}).get("siteConfig", {}).get("phpVersion")
            expected_values = self.get_expected_value()
            if php_version in expected_values:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = AppServicePHPVersion()

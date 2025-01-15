from typing import Any, List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class FunctionAppMinTLSVersion(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Function app is using the latest version of TLS encryption"
        id = "CKV_AZURE_145"
        supported_resources = ('Microsoft.Web/sites', 'Microsoft.Web/sites/slots',)
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self) -> str:
        return "properties/siteConfig/minTlsVersion"

    def get_expected_value(self) -> Any:
        return 1.2

    def get_expected_values(self) -> List[Any]:
        return ["1.2", 1.2, "1.3", 1.3]


check = FunctionAppMinTLSVersion()

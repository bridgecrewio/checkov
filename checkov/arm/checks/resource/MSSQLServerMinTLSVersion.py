from typing import List, Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class MSSQLServerMinTLSVersion(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure MSSQL is using the latest version of TLS encryption"
        id = "CKV_AZURE_52"
        supported_resources = ("Microsoft.Sql/servers",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name,
                         id=id,
                         categories=categories,
                         supported_resources=supported_resources,
                         missing_block_result=CheckResult.FAILED,)

    def get_inspected_key(self) -> str:
        return "properties/minimalTlsVersion"

    def get_expected_value(self) -> str:
        return "1.2"

    def get_expected_values(self) -> List[Any]:
        return ["1.2", 1.2, "1.3", 1.3]


check = MSSQLServerMinTLSVersion()

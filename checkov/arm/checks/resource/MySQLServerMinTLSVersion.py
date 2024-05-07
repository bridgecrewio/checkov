from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class MySQLServerMinTLSVersion(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure MySQL is using the latest version of TLS encryption"
        id = "CKV_AZURE_54"
        supported_resources = ("Microsoft.DBforMySQL/servers",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name,
                         id=id,
                         categories=categories,
                         supported_resources=supported_resources, )

    def get_inspected_key(self) -> str:
        return "properties/minimalTlsVersion"

    def get_expected_value(self) -> str:
        return "TLS1_2"


check = MySQLServerMinTLSVersion()

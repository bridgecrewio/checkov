from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class PostgreSQLEncryptionEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that PostgreSQL server enables infrastructure encryption"
        id = "CKV_AZURE_130"
        supported_resources = ["Microsoft.DBforPostgreSQL/servers"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/infrastructureEncryption"

    def get_expected_value(self) -> str:
        return "Enabled"


check = PostgreSQLEncryptionEnabled()

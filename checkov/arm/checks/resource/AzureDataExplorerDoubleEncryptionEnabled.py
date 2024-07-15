from typing import Any
from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class AzureDataExplorerDoubleEncryptionEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name: str = "Ensure that Azure Data Explorer uses double encryption"
        id: str = "CKV_AZURE_75"
        supported_resources = ("Microsoft.Kusto/clusters",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/enableDoubleEncryption"

    def get_expected_value(self) -> Any:
        return True


check: Any = AzureDataExplorerDoubleEncryptionEnabled()

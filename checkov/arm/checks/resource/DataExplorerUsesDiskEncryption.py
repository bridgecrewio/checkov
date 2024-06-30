from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class DataExplorerUsesDiskEncryption(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure Data Explorer (Kusto) uses disk encryption"
        id = "CKV_AZURE_74"
        supported_resources = ("Microsoft.Kusto/clusters",)
        categories = [CheckCategories.ENCRYPTION,]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,)

    def get_inspected_key(self) -> str:
        return "properties/enableDiskEncryption"

    def get_expected_value(self) -> bool:
        return True


check = DataExplorerUsesDiskEncryption()

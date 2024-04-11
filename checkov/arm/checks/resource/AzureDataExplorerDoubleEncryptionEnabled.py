from typing import Any
from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class AzureDataExplorerDoubleEncryptionEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that Azure Data Explorer uses double encryption"
        id = "CKV_AZURE_75"
        supported_resources = ("Microsoft.Compute/disks",)
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "properties/doubleEncryptionEnabled"

    def get_expected_value(self):
        return True


check = AzureDataExplorerDoubleEncryptionEnabled()


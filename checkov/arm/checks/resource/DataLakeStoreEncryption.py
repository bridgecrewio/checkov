from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class DataLakeStoreEncryption(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Data Lake Store accounts enables encryption"
        id = "CKV_AZURE_105"
        supported_resources = ['Microsoft.DataLakeStore/accounts',]
        categories = [CheckCategories.ENCRYPTION,]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources, missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self) -> str:
        return 'properties/encryptionState'

    def get_expected_value(self) -> str:
        return "Enabled"


check = DataLakeStoreEncryption()

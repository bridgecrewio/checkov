from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class DataLakeStoreEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that Data Lake Store accounts enables encryption"
        id = "CKV_AZURE_105"
        supported_resources = ['azurerm_data_lake_store']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources, missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self):
        return 'encryption_state'

    def get_expected_value(self):
        return "Enabled"


check = DataLakeStoreEncryption()

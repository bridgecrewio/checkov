from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class StorageAccountEnablesSecureTransfer(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that storage account enables secure transfer"
        id = "CKV_AZURE_60"
        supported_resources = ['azurerm_storage_account']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self):
        return "enable_https_traffic_only"


check = StorageAccountEnablesSecureTransfer()

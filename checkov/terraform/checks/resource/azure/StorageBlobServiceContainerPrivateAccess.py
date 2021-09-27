from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class StorageBlobServiceContainerPrivateAccess(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that 'Public access level' is set to Private for blob containers"
        id = "CKV_AZURE_34"
        supported_resources = ['azurerm_storage_container']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self):
        return 'container_access_type/[0]'

    def get_expected_value(self):
        return 'private'


check = StorageBlobServiceContainerPrivateAccess()

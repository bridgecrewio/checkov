from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class StorageLocalUsers(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Avoid the use of local users for Azure Storage unless necessary"
        id = "CKV_AZURE_244"
        supported_resources = ('azurerm_storage_account',)
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'local_user_enabled'

    def get_expected_value(self) -> bool:
        return False


check = StorageLocalUsers()

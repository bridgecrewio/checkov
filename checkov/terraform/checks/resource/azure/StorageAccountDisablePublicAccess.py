from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class StorageAccountDisablePublicAccess(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure that Storage accounts disallow public access"
        id = "CKV_AZURE_59"
        supported_resources = ['azurerm_storage_account']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "allow_blob_public_access"

    def get_forbidden_values(self):
        return [True]


check = StorageAccountDisablePublicAccess()

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class StorageBlobRestrictPublicAccess(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure that Storage blobs restrict public access"
        id = "CKV_AZURE_190"
        supported_resources = ['azurerm_storage_account']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_attribute_result=CheckResult.FAILED)

    def get_inspected_key(self):
        return "allow_nested_items_to_be_public"

    def get_forbidden_values(self):
        return [True]


check = StorageBlobRestrictPublicAccess()

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck



class CosmosDBDisableAccessKeyWrite(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure cosmosdb does not allow privileged escalation by restricting management plane changes"
        id = "CKV_AZURE_132"
        supported_resources = ['azurerm_cosmosdb_account']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'access_key_metadata_writes_enabled'

    def get_expected_value(self):
        return False


check = CosmosDBDisableAccessKeyWrite()


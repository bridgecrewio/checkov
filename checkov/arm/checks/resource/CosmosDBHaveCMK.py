from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class CosmosDBHaveCMK(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that Cosmos DB accounts have customer-managed keys to encrypt data at rest"
        id = "CKV_AZURE_100"
        supported_resources = ['Microsoft.DocumentDb/databaseAccounts']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'properties/keyVaultKeyUri'

    def get_expected_value(self):
        return ANY_VALUE


check = CosmosDBHaveCMK()

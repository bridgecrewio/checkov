from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_value_check import BaseResourceValueCheck


class CosmosDBDisablesPublicNetwork(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure Cosmos DB disables public network access"
        id = "CKV_AZURE_101"
        supported_resources = ['Microsoft.DocumentDB/databaseAccounts']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'properties/publicNetworkAccess'

    def get_expected_value(self) -> str:
        return "Disabled"


check = CosmosDBDisablesPublicNetwork()

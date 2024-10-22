from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class DataExplorerServiceIdentity(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that data explorer/Kusto uses managed identities to access Azure resources securely."
        id = "CKV_AZURE_181"
        supported_resources = ('azurerm_kusto_cluster',)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'identity/[0]/type'

    def get_expected_values(self) -> Any:
        return ANY_VALUE


check = DataExplorerServiceIdentity()

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AzureSqlPoolEncryption(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Synapse SQL pools are encrypted"
        id = "CKV_AZURE_241"
        supported_resources = ("synapse_sql_pool",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "data_encrypted"


check = AzureSqlPoolEncryption()

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class StorageAccountsTransportEncryption(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that 'enable_https_traffic_only' is enabled"
        id = "CKV_AZURE_3"
        supported_resources = ("azurerm_storage_account",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
            missing_block_result=CheckResult.PASSED,
        )

    def get_inspected_key(self) -> str:
        return "enable_https_traffic_only"


check = StorageAccountsTransportEncryption()

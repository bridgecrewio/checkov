from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class StorageLocalUsers(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Avoid the use of local users for Azure Storage unless necessary"
        id = "CKV_AZURE_244"
        supported_resources = ('azurerm_storage_account',)
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict) -> CheckResult:
        # If local_user_enabled is explicitly True, return the default check result
        local_user_enabled = conf.get("local_user_enabled")
        if local_user_enabled is not None or local_user_enabled:
            return super().scan_resource_conf(conf)

        # Else only check if SFTP is enabled, which requires is_hns_enabled to exist and be True
        hns_enabled = conf.get("is_hns_enabled")
        if hns_enabled is None or not hns_enabled:
            return CheckResult.PASSED
        return super().scan_resource_conf(conf)

    def get_inspected_key(self) -> str:
        return 'local_user_enabled'

    def get_expected_value(self) -> bool:
        return False


check = StorageLocalUsers()

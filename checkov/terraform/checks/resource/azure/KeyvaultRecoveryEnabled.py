from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck
from typing import List


class KeyVaultRecoveryEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure the key vault is recoverable"
        id = "CKV_AZURE_42"
        supported_resources = ['azurerm_key_vault']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'purge_protection_enabled' in conf and conf['purge_protection_enabled'][0] and \
                ('soft_delete_enabled' not in conf or conf['soft_delete_enabled'][0]):
            return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ['purge_protection_enabled', 'soft_delete_enabled']


check = KeyVaultRecoveryEnabled()

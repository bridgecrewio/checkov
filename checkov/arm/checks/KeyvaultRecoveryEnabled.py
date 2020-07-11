from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck

# https://docs.microsoft.com/en-us/azure/templates/microsoft.keyvault/2016-10-01/vaults

class KeyVaultRecoveryEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure the key vault is recoverable"
        id = "CKV_AZURE_42"
        supported_resources = ['Microsoft.KeyVault/vaults']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # NOTE: enablePurgeProtection not supported in API version 2015-06-01
        if "properties" in conf:
            if "enablePurgeProtection" in conf["properties"] and "enableSoftDelete" in conf["properties"]:
                if str(conf["properties"]["enablePurgeProtection"]).lower() == "true" and \
                        str(conf["properties"]["enableSoftDelete"]).lower() == "true":
                    return CheckResult.PASSED
        return CheckResult.FAILED

check = KeyVaultRecoveryEnabled()

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AzureDiskEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Disks are encrypted at rest"
        id = "CKV_AZURE_51"
        supported_resources = ['azurerm_managed_disk']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'disk_encryption_set_id' in conf:
            return CheckResult.PASSED
        if 'encryption_settings' in conf:
            if isinstance(conf['encryption_settings'][0], dict):
                return CheckResult.PASSED if conf['encryption_settings'][0]['enabled'][0] else CheckResult.FAILED
        return CheckResult.FAILED

check = AzureDiskEncryption()

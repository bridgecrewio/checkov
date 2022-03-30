from checkov.common.models.enums import CheckCategories,CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class DiskEncryptedWithCMK(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Disk is encrypted with Customer Master Key"
        id = "CKV_ALI_8"
        supported_resources = ['alicloud_disk']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get("snapshot_id"):
            return CheckResult.UNKNOWN
        if conf.get("encrypted") and conf.get("encrypted") == [True]:
            if conf.get("kms_key_id"):
                return CheckResult.PASSED
        return CheckResult.FAILED


check = DiskEncryptedWithCMK()

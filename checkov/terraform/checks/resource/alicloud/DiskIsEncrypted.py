from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class DiskIsEncrypted(BaseResourceCheck):
    def __init__(self):
        name = "Ensure disk is encrypted"
        id = "CKV_ALI_7"
        supported_resources = ['alicloud_disk']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get("snapshot_id"):
            return CheckResult.UNKNOWN
        if conf.get("encrypted") and conf.get("encrypted") == [True]:
            return CheckResult.PASSED
        return CheckResult.FAILED


check = DiskIsEncrypted()

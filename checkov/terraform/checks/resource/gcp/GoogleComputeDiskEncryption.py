from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class GoogleComputeDiskEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure VM disks for critical VMs are encrypted with Customer Supplied Encryption Keys (CSEK)"
        id = "CKV_GCP_37"
        supported_resources = ['google_compute_disk']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'disk_encryption_key' in conf.keys():
            if len(conf['disk_encryption_key'][0]) > 0:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = GoogleComputeDiskEncryption()

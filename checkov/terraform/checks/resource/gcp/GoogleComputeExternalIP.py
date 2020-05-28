from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class GoogleComputeExternalIP(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that Compute instances do not have public IP addresses"
        id = "CKV_GCP_40"
        supported_resources = ['google_compute_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'access_config' in conf.keys():
            return CheckResult.FAILED
        return CheckResult.PASSED

check = GoogleComputeExternalIP()

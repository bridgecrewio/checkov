from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class GoogleComputeExternalIP(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure that Compute instances do not have public IP addresses"
        id = "CKV_GCP_40"
        supported_resources = ['google_compute_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        inspected_key = self.get_inspected_key()
        if inspected_key in conf.keys():
            return CheckResult.FAILED
        return CheckResult.PASSED

    def get_inspected_key(self):
        return 'access_config'


check = GoogleComputeExternalIP()

from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class GoogleSubnetworkLoggingEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that VPC Flow Logs is enabled for every subnet in a VPC Network"
        id = "CKV_GCP_26"
        supported_resources = ['google_compute_subnetwork']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'log_config' in conf:
            return CheckResult.PASSED
        return CheckResult.FAILED


check = GoogleSubnetworkLoggingEnabled()

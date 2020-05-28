from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class GoogleComputeIPForward(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that IP forwarding is not enabled on Instances"
        id = "CKV_GCP_36"
        supported_resources = ['google_compute_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # Instances created by GKE should be excluded because they need to have IP forwarding enabled
        if conf['name'][0].startswith('gke-'):
            return CheckResult.PASSED
        elif 'can_ip_forward' in conf.keys():
            if conf['can_ip_forward'][0]:
                return CheckResult.FAILED
        return CheckResult.PASSED


check = GoogleComputeIPForward()

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

PORT = '22'


class GoogleComputeFirewallUnrestrictedIngress22(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Google compute firewall ingress does not allow unrestricted ssh access"
        id = "CKV_GCP_2"
        supported_resources = ['google_compute_firewall']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for password configuration at google_compute_firewall:
            https://www.terraform.io/docs/providers/google/r/compute_firewall.html
        :param conf: azure_instance configuration
        :return: <CheckResult>
        """
        if 'allow' in conf:
            allow_blocks = conf['allow']
            for block in allow_blocks:
                if 'ports' in block.keys():
                    if PORT in block['ports'][0]:
                        if 'source_ranges' in conf.keys():
                            source_ranges = conf['source_ranges'][0]
                            if "0.0.0.0/0" in source_ranges:
                                return CheckResult.FAILED
        return CheckResult.PASSED


check = GoogleComputeFirewallUnrestrictedIngress22()

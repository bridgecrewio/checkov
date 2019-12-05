from checkov.terraform.models.enums import ScanResult, ScanCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck

PORT = '22'


class GoogleComputeFirewallUnrestrictedIngress22(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Google compute firewall ingress does not allow unrestricted ssh access"
        scan_id = "BC_GCP_NETWORKING_1"
        supported_resources = ['google_compute_firewall']
        categories = [ScanCategories.NETWORKING]
        super().__init__(name=name, scan_id=scan_id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for password configuration at google_compute_firewall:
            https://www.terraform.io/docs/providers/google/r/compute_firewall.html
        :param conf: azure_instance configuration
        :return: <ScanResult>
        """
        if PORT in conf['allow'][0]['ports'][0]:
            if 'source_ranges' in conf.keys():
                source_ranges = conf['source_ranges'][0]
                if "0.0.0.0/0" in source_ranges:
                    return ScanResult.FAILURE
        return ScanResult.SUCCESS


scanner = GoogleComputeFirewallUnrestrictedIngress22()

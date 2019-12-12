from checkov.terraform.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck


class GoogleComputeMinTLSVersion(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Google SSL policy minimal TLS version is TLS_1_2"
        id = "CKV_GCP_4"
        supported_resources = ['google_compute_ssl_policy']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for password configuration at azure_instance:
            https://www.terraform.io/docs/providers/google/r/compute_ssl_policy.html
        :param conf: google_compute_ssl_policy configuration
        :return: <CheckResult>
        """
        if 'min_tls_version' in conf.keys():
            if conf['min_tls_version'][0] == "TLS_1_2":
                return CheckResult.PASSED
        return CheckResult.FAILED


check = GoogleComputeMinTLSVersion()

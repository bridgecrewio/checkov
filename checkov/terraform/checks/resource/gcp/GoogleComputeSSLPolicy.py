from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class GoogleComputeSSLPolicy(BaseResourceCheck):
    def __init__(self):
        name = "Ensure no HTTPS or SSL proxy load balancers permit SSL policies with weak cipher suites"
        id = "CKV_GCP_4"
        supported_resources = ['google_compute_ssl_policy']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            https://www.terraform.io/docs/providers/google/r/compute_ssl_policy.html
        :param conf: google_compute_ssl_policy configuration
        :return: <CheckResult>
        """
        if 'profile' in conf.keys():
            self.evaluated_keys = ['profile']
            if conf['profile'][0] == 'RESTRICTED':
                return CheckResult.PASSED
            elif conf['profile'][0] == 'MODERN':
                if 'min_tls_version' in conf.keys():
                    self.evaluated_keys.append('min_tls_version')
                    if conf['min_tls_version'][0] == "TLS_1_2":
                        return CheckResult.PASSED
            elif conf['profile'][0] == 'CUSTOM':
                self.evaluated_keys.append('custom_features')
                if not any(item in conf['custom_features'][0] for item in ['TLS_RSA_WITH_AES_128_GCM_SHA256',
                                                                           'TLS_RSA_WITH_AES_256_GCM_SHA384',
                                                                           'TLS_RSA_WITH_AES_128_CBC_SHA',
                                                                           'TLS_RSA_WITH_AES_256_CBC_SHA',
                                                                           'TLS_RSA_WITH_3DES_EDE_CBC_SHA']):
                    return CheckResult.PASSED
        return CheckResult.FAILED


check = GoogleComputeSSLPolicy()

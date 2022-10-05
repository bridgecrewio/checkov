from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class LBSecureProtocols(BaseResourceCheck):
    def __init__(self):
        name = "Ensure ELB Policy uses only secure protocols"
        id = "CKV_NCP_213"
        supported_resources = ['ncloud_lb_listener']

        categories = [CheckCategories.NETWORKING]
        guideline = "You should Ensure ELB Policy uses only secure protocols"
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources, guideline=guideline)

    def scan_resource_conf(self, conf):
        protocol = conf['protocol'][0]
        if protocol == 'HTTPS' or protocol == 'TLS':
            if 'tls_min_version_type' in conf.keys():
                TLSVersion = conf['tls_min_version_type'][0]
                if TLSVersion == 'TLSV12':
                    return CheckResult.PASSED
        return CheckResult.FAILED


check = LBSecureProtocols()

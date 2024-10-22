
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class LBListenerUsesSecureProtocols(BaseResourceCheck):
    def __init__(self):
        name = "Ensure LB Listener uses only secure protocols"
        id = "CKV_NCP_13"
        supported_resources = ('ncloud_lb_listener',)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'protocol' in conf.keys():
            protocol = conf['protocol'][0]
            if protocol in ('HTTPS', 'TLS'):
                if 'tls_min_version_type' in conf.keys():
                    if conf['tls_min_version_type'] == ['TLSV12']:
                        return CheckResult.PASSED
            return CheckResult.FAILED


check = LBListenerUsesSecureProtocols()

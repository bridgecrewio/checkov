
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class NCP_LBListenerTLS12(BaseResourceCheck):

    def __init__(self):
        name = "Ensure that Load Balancer Listener is using at least TLS v1.2"
        id = "CKV_AWS_3"
        supported_resources = ['ncloud_lb_listener']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # Check SslPolicy only if protocol is HTTPS (ALB) or TLS (NLB).
        # Other protocols are not interesting within the context of this check.
        if 'protocol' in conf.keys():
            protocol = conf['protocol'][0]
            if protocol in ('HTTPS', 'TLS'):
                if 'tls_min_version_type' in conf.keys():
                    if conf['tls_min_version_type'][0] == 'TLSV12':
                        return CheckResult.PASSED
                return CheckResult.FAILED
            else:
                return CheckResult.UNKNOWN

check = NCP_LBListenerTLS12()
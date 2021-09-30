from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ELBUsesSSL(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that Elastic Load Balancer(s) uses SSL certificates provided by AWS Certificate Manager"
        id = "CKV_AWS_127"
        supported_resources = ['aws_elb']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        self.evaluated_keys = ['listener']
        if 'listener' in conf:
            for idx, listener in enumerate(conf['listener']):
                if 'ssl_certificate_id' not in listener:
                    self.evaluated_keys = [f'listener/{idx}']
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = ELBUsesSSL()

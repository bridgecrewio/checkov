from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class ELBAccessLogs(BaseResourceCheck):
    def __init__(self):
        name = "Ensure the ELB has access logging enabled"
        id = "CKV_AWS_92"
        supported_resources = ['aws_elb']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        self.evaluated_keys = 'access_logs'
        if 'access_logs' in conf:
            if 'enabled' not in conf['access_logs'][0]:
                return CheckResult.PASSED
            self.evaluated_keys = 'access_logs/[0]/enabled'
            if conf['access_logs'][0]['enabled'] == [True]:
                return CheckResult.PASSED
        return CheckResult.FAILED

check = ELBAccessLogs()

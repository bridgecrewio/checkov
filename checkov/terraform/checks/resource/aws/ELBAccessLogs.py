from typing import List

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
        if 'access_logs' not in conf:
            return CheckResult.FAILED
        if 'enabled' not in conf['access_logs'][0]:
            return CheckResult.PASSED
        if conf['access_logs'][0]['enabled'] == [True]:
            return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ["access_logs/[0]/enabled"]


check = ELBAccessLogs()

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

class ELBv2AccessLogs(BaseResourceCheck):
    def __init__(self):
        name = "Ensure the ELBv2 (Application/Network) has access logging enabled"
        id = "CKV_AWS_91"
        supported_resources = ['aws_lb', 'aws_alb']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if ('access_logs' in conf) and ('enabled' in conf['access_logs'][0]) and (conf['access_logs'][0]['enabled'] == [True]):
            return CheckResult.PASSED
        return CheckResult.FAILED

check = ELBv2AccessLogs()

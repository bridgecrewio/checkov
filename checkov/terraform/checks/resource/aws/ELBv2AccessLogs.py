from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class ELBv2AccessLogs(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure the ELBv2 (Application/Network) has access logging enabled"
        id = "CKV_AWS_91"
        supported_resources = ['aws_lb', 'aws_alb']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'access_logs/0/enabled/0'


check = ELBv2AccessLogs()

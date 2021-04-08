from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class ALBDropHttpHeaders(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure that ALB drops HTTP headers"
        id = "CKV_AWS_131"
        supported_resources = ['aws_lb', 'aws_alb']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get('load_balancer_type') == 'network':
            return CheckResult.UNKNOWN
        return super().scan_resource_conf(conf)

    def get_inspected_key(self):
        return 'drop_invalid_header_fields'


check = ALBDropHttpHeaders()

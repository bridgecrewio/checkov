from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_list
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AutoScalingGroupWithPublicAccess(BaseResourceCheck):

    def __init__(self):
        name = "AWS Auto Scaling group launch configuration has public IP address assignment enabled"
        id = "CKV_AWS_389"
        supported_resources = ['aws_launch_configuration']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'associate_public_ip_address' in conf:
            if str(conf['associate_public_ip_address'][0]).lower() == 'true':
                return CheckResult.FAILED
        return CheckResult.PASSED


check = AutoScalingGroupWithPublicAccess()

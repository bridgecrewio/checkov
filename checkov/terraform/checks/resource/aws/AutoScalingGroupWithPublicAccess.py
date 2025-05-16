from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class AutoScalingGroupWithPublicAccess(BaseResourceNegativeValueCheck):

    def __init__(self):
        name = "Ensure AWS Auto Scaling group launch configuration doesn't have public IP address assignment enabled"
        id = "CKV_AWS_389"
        supported_resources = ['aws_launch_configuration']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_forbidden_values(self):
        return [True]

    def get_inspected_key(self):
        return "associate_public_ip_address"


check = AutoScalingGroupWithPublicAccess()

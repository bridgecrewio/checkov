from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckCategories


class ALBDesyncMode(BaseResourceNegativeValueCheck):
    def __init__(self):
        """
        NIST.800-53.r5 AC-4(21), NIST.800-53.r5 CA-9(1), NIST.800-53.r5 CM-2
        Classic Load Balancer and ALB should be configured with defensive or strictest desync mitigation mode
        """
        name = "Ensure that ALB is configured with defensive or strictest desync mitigation mode"
        id = "CKV_AWS_328"
        supported_resources = ["aws_lb", "aws_alb", "aws_elb"]
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "desync_mitigation_mode"

    def get_forbidden_values(self):
        return "monitor"


check = ALBDesyncMode()

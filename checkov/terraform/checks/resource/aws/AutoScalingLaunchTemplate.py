from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class AutoScalingLaunchTemplate(BaseResourceValueCheck):
    def __init__(self) -> None:
        """
        NIST.800-53.r5 CA-9(1), NIST.800-53.r5 CM-2, NIST.800-53.r5 CM-2(2)
        EC2 Auto Scaling groups should use EC2 launch templates
        """
        name = "Ensure EC2 Auto Scaling groups use EC2 launch templates"
        id = "CKV_AWS_315"
        supported_resources = ("aws_autoscaling_group",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "launch_template"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = AutoScalingLaunchTemplate()

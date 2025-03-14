from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class AutoScalingLaunchTemplate(BaseResourceCheck):
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

    def scan_resource_conf(self, conf) -> CheckResult:
        if "launch_template" in conf:
            return CheckResult.PASSED

        if "mixed_instances_policy" in conf and "launch_template" in conf["mixed_instances_policy"][0]:
            return CheckResult.PASSED

        return CheckResult.FAILED


check = AutoScalingLaunchTemplate()

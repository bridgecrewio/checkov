from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckCategories


class CloudWatchAlarmsEnabled(BaseResourceNegativeValueCheck):
    def __init__(self):
        """
        NIST.800-53.r5 AU-6(1), NIST.800-53.r5 AU-6(5), NIST.800-53.r5 CA-7,
        NIST.800-53.r5 SI-2, NIST.800-53.r5 SI-4(12)
        CloudWatch alarm actions should be activated
        """
        name = "Ensure that CloudWatch alarm actions are enabled"
        id = "CKV_AWS_319"
        supported_resources = ['aws_cloudwatch_metric_alarm']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "actions_enabled"

    def get_forbidden_values(self):
        return [False]


check = CloudWatchAlarmsEnabled()

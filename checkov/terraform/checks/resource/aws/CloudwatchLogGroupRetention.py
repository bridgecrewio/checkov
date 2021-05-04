from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class CloudwatchLogGroupRetention(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure cloudwatch log groups specify retention days"
        id = "CKV_AWS_66"
        supported_resource = ['aws_cloudwatch_log_group']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resource)

    def get_inspected_key(self):
        return "retention_in_days"

    def get_expected_value(self):
        return ANY_VALUE


check = CloudwatchLogGroupRetention()

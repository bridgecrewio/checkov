from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class CloudformationStackNotificationArns(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that CloudFormation stacks are sending event notifications to an SNS topic"
        id = "CKV_AWS_124"
        supported_resources = ['aws_cloudformation_stack']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'notification_arns'

    def get_expected_value(self):
        return ANY_VALUE


check = CloudformationStackNotificationArns()

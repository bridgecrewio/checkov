from checkov.common.models.consts import ANY_VALUE
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class CloudwatchLogGroupKMSKey(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that CloudWatch Group is encrypted by KMS"
        id = "CKV_AWS_158"
        supported_resources = ['aws_cloudwatch_log_group']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "kms_key_id"

    def get_expected_value(self):
        return ANY_VALUE


check = CloudwatchLogGroupKMSKey()

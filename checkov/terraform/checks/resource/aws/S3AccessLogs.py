from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class S3AccessLogs(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure the S3 bucket has access logging enabled"
        id = "CKV_AWS_18"
        supported_resources = ['aws_s3_bucket']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'logging'

    def get_expected_value(self):
        return ANY_VALUE


check = S3AccessLogs()

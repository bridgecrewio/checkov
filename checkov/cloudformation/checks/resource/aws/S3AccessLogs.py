from typing import Any

from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories


class S3AccessLogs(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure the S3 bucket has access logging enabled"
        id = "CKV_AWS_18"
        supported_resources = ['AWS::S3::Bucket']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/LoggingConfiguration"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = S3AccessLogs()

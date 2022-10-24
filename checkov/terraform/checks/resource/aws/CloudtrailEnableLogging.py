from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class CloudtrailEnableLogging(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure CloudTrail logging is enabled"
        id = "CKV_AWS_251"
        supported_resources = ['aws_cloudtrail']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self):
        return "enable_logging"


check = CloudtrailEnableLogging()

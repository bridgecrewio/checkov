from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class CloudtrailLogValidation(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure CloudTrail log file validation is enabled"
        id = "CKV_AWS_36"
        supported_resources = ['aws_cloudtrail']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "enable_log_file_validation"


check = CloudtrailLogValidation()

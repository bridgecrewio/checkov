from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class GuarddutyDetectorEnabled(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure that GuardDuty detector is enabled"
        id = "CKV_AWS_238"
        supported_resources = ['aws_guardduty_detector']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self):
        return 'enable'


check = GuarddutyDetectorEnabled()

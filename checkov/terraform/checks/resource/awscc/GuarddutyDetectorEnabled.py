from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class GuarddutyDetectorEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure GuardDuty detector is enabled"
        id = "CKV_AWS_118"
        supported_resources = ['awscc_guardduty_detector']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "enable"


check = GuarddutyDetectorEnabled()

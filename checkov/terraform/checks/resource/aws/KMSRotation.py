from checkov.terraform.checks.resource.BaseResourceBooleanValueCheck import BaseResourceBooleanValueCheck
from checkov.terraform.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck


class KMSRotation(BaseResourceBooleanValueCheck):
    def __init__(self):
        name = "Ensure rotation for customer created CMKs is enabled"
        id = "CKV_AWS_7"
        supported_resources = ['aws_kms_key']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "enable_key_rotation"


check = KMSRotation()

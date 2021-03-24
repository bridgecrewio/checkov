from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class KMSKeyRotation(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure KMS have rotation policy"
        id = "CKV_AWS_132"
        supported_resources = ['aws_kms_key']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "enable_key_rotation"


check = KMSKeyRotation()

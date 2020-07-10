from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class PasswordPolicyLowercaseLetter(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure IAM password policy requires at least one lowercase letter"
        id = "CKV_AWS_11"
        supported_resources = ['aws_iam_account_password_policy']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'require_lowercase_characters'


check = PasswordPolicyLowercaseLetter()

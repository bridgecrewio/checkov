from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class PasswordPolicyUppcaseLetter(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure IAM password policy requires at least one uppercase letter"
        id = "CKV_AWS_15"
        supported_resources = ['aws_iam_account_password_policy']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'require_uppercase_characters'


check = PasswordPolicyUppcaseLetter()

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class PasswordPolicyNumber(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure RAM password policy requires at least one number"
        id = "CKV_ALI_14"
        supported_resources = ['alicloud_ram_account_password_policy']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'require_numbers'


check = PasswordPolicyNumber()

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class IAMPasswordPolicySpecialCharacters(BaseResourceValueCheck):
    def __init__(self):
        name = "OCI IAM password policy - must contain Uppercase characters"
        id = "CKV_OCI_14"
        supported_resources = ['oci_identity_authentication_policy']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'password_policy/[0]/is_uppercase_characters_required'

    def get_expected_value(self):
        return True


check = IAMPasswordPolicySpecialCharacters()

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class CognitoUserPoolAdvancedSecurityEnforced(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Cognito user pool advanced security mode is ENFORCED"
        id = "CKV_AWS_398"
        supported_resources = ["aws_cognito_user_pool"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def get_inspected_key(self):
        return "user_pool_add_ons/[0]/advanced_security_mode"

    def get_expected_value(self):
        return "ENFORCED"


check = CognitoUserPoolAdvancedSecurityEnforced()

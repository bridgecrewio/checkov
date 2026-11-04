from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class CognitoUserPoolAdvancedSecurityEnforced(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Cognito user pool advanced security mode is ENFORCED"
        id = "CKV_AWS_398"
        supported_resources = ('AWS::Cognito::UserPool',)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
            missing_block_result=CheckResult.FAILED,
        )

    def get_expected_value(self) -> Any:
        return "ENFORCED"

    def get_inspected_key(self) -> str:
        return 'Properties/UserPoolAddOns/AdvancedSecurityMode'


check = CognitoUserPoolAdvancedSecurityEnforced()

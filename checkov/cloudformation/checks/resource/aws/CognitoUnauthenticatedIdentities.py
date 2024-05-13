from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class CognitoUnauthenticatedIdentities(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure AWS Cognito identity pool does not allow unauthenticated guest access"
        id = "CKV_AWS_366"
        supported_resources = ('AWS::Cognito::IdentityPool',)
        categories = (CheckCategories.IAM,)
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
            missing_block_result=CheckResult.FAILED,
        )

    def get_expected_value(self) -> Any:
        return False

    def get_inspected_key(self) -> str:
        return 'Properties/AllowUnauthenticatedIdentities'


check = CognitoUnauthenticatedIdentities()

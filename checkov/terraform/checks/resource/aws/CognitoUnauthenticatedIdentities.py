from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class CloudsearchDomainEnforceHttps(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure AWS Cognito identity pool does not allow unauthenticated guest access"
        id = "CKV_AWS_366"
        supported_resources = ["aws_cognito_identity_pool"]
        categories = [CheckCategories.IAM]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def get_inspected_key(self) -> str:
        return "allow_unauthenticated_identities"

    def get_expected_value(self) -> bool:
        return False


check = CloudsearchDomainEnforceHttps()

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from typing import Any, List


class APIGatewayDomainNameTLS(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure API Gateway Domain uses a modern security Policy"
        id = "CKV_AWS_206"
        supported_resources = ["aws_api_gateway_domain_name"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def get_inspected_key(self) -> str:
        return "security_policy"

    def get_expected_values(self) -> List[Any]:
        return ["TLS_1_2"]


check = APIGatewayDomainNameTLS()

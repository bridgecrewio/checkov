from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from typing import Any, List


class APIGatewayV2RouteDefinesAuthorizationType(BaseResourceValueCheck):

    def __init__(self):
        """
        NIST.800-53.r5 AC-3, NIST.800-53.r5 CM-2, NIST.800-53.r5 CM-2(2)
        """
        name = "Ensure API GatewayV2 routes specify an authorization type"
        id = "CKV_AWS_309"
        supported_resources = ['aws_apigatewayv2_route']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "authorization_type"

    def get_expected_values(self) -> List[Any]:
        return ["AWS_IAM", "CUSTOM", "JWT"]


check = APIGatewayV2RouteDefinesAuthorizationType()

from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE


class APIGatewayAccessLogging(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure API Gateway has Access Logging enabled"
        id = "CKV_AWS_76"
        supported_resources = ['aws_api_gateway_stage', 'aws_apigatewayv2_stage']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "access_log_settings/[0]/destination_arn"

    def get_expected_value(self):
        return ANY_VALUE


check = APIGatewayAccessLogging()

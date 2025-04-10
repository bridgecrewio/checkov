from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class APIGatewayXray(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure API Gateway has X-Ray tracing enabled"
        id = "CKV_AWS_73"
        supported_resources = ['awscc_apigateway_stage']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "tracing_enabled"
        
    def get_expected_value(self):
        return True


check = APIGatewayXray()

from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckCategories


class APIGatewayMethodSettingsDataTrace(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure Data Trace is not enabled in API Gateway Method Settings"
        id = "CKV_AWS_276"
        supported_resources = ('aws_api_gateway_method_settings',)
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "settings/[0]/data_trace_enabled"

    def get_forbidden_values(self):
        return [True]


check = APIGatewayMethodSettingsDataTrace()

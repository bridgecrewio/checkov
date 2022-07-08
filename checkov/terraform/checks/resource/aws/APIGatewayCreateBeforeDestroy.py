from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class APIGatewayCreateBeforeDestroy(BaseResourceValueCheck):

    def __init__(self):
        """
        It is recommended to enable the resource lifecycle configuration block create_before_destroy
        argument in this resource configuration to manage all requests that use this API, avoiding an outage.
        """
        name = "Ensure Create before destroy for API GATEWAY"
        id = "CKV_AWS_237"
        supported_resources = ['aws_api_gateway_rest_api']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "lifecycle/[0]/create_before_destroy"


check = APIGatewayCreateBeforeDestroy()

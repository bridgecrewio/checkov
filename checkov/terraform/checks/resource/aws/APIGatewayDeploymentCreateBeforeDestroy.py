from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class APIGatewayDeploymentCreateBeforeDestroy(BaseResourceValueCheck):

    def __init__(self):
        """
        It is recommended to enable the resource lifecycle configuration block create_before_destroy
        argument in this resource configuration to properly order redeployments in Terraform.
        Without enabling create_before_destroy, API Gateway can return errors such as BadRequestException:
        Active stages pointing to this deployment must be moved or deleted on recreation.
        """
        name = "Ensure Create before destroy for API deployments"
        id = "CKV_AWS_217"
        supported_resources = ['aws_api_gateway_deployment']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "lifecycle/[0]/create_before_destroy"


check = APIGatewayDeploymentCreateBeforeDestroy()

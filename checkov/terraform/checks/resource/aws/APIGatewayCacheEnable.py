from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class APIGatewayCacheEnable(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure API Gateway caching is enabled"
        id = "CKV_AWS_120"
        supported_resources = ['aws_api_gateway_stage']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "cache_cluster_enabled"


check = APIGatewayCacheEnable()

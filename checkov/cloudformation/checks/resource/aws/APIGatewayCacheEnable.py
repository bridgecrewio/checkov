from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE


class APIGatewayCacheEnable(BaseResourceValueCheck):
    
    def __init__(self):
        name = "Ensure API Gateway caching is enabled"
        id = "CKV_AWS_120"
        supported_resources = ['AWS::ApiGateway::Stage']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'Properties/CacheClusterEnabled'


check = APIGatewayCacheEnable()

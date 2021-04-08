from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class RedisCachePublicNetworkAccessEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that Azure Cache for Redis disables public network access"
        id = "CKV_AZURE_89"
        supported_resources = ['azurerm_redis_cache']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'public_network_access_enabled'

    def get_expected_value(self):
        return False


check = RedisCachePublicNetworkAccessEnabled()

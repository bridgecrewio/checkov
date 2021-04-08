from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class RedisCacheEnableNonSSLPort(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that only SSL are enabled for Cache for Redis"
        id = "CKV_AZURE_91"
        supported_resources = ['azurerm_redis_cache']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.PASSED)

    def get_inspected_key(self):
        return "enable_non_ssl_port"

    def get_expected_value(self):
        return False


check = RedisCacheEnableNonSSLPort()

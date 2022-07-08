from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class RedisCacheMinTLSVersion(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Redis Cache is using the latest version of TLS encryption"
        id = "CKV_AZURE_148"
        supported_resources = ['azurerm_redis_cache']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.FAILED)

    def get_inspected_key(self):
        return "minimum_tls_version"

    def get_expected_value(self):
        return '1.2'


check = RedisCacheMinTLSVersion()

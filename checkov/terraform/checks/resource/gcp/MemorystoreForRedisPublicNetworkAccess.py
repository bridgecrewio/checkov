from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class MemorystoreForRedisPublicNetworkAccess(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Memorystore for Redis is not exposed to public internet"
        id = "CKV_GCP_99"
        supported_resources = ['google_redis_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'connect_mode' in conf and conf['connect_mode'][0] == 'DIRECT_PEERING':
            return CheckResult.FAILED
        return CheckResult.PASSED


check = MemorystoreForRedisPublicNetworkAccess()

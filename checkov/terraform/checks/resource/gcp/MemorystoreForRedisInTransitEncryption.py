from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class MemorystoreForRedisInTransitEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Memorystore for Redis uses intransit encryption"
        id = "CKV_GCP_97"
        supported_resources = ['google_redis_instance']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "transit_encryption_mode"

    # Accounts for if key is present but is set to False
    def get_expected_value(self):
        return "SERVER_AUTHENTICATION"


check = MemorystoreForRedisInTransitEncryption()

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class ElasticacheReplicationGroupEncryptionAtRest(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure ElastiCache ReplicationGroup has encryption at rest enabled"
        id = "CKV_AWS_29"
        supported_resources = ("awscc_elasticache_global_replication_group",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "at_rest_encryption_enabled"

    def get_expected_value(self):
        return True


check = ElasticacheReplicationGroupEncryptionAtRest()

from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class ElasticacheReplicationGroupEncryptionAtTransit(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure all data stored in the Elasticache Replication Group  is securely encrypted at transit"
        id = "CKV_AWS_30"
        supported_resources = ['aws_elasticache_replication_group']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "transit_encryption_enabled"


check = ElasticacheReplicationGroupEncryptionAtTransit()

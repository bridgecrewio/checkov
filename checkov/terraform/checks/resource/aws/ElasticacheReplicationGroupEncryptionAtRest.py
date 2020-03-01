from checkov.terraform.checks.resource.BaseResourceBooleanValueCheck import BaseResourceBooleanValueCheck
from checkov.terraform.models.enums import CheckCategories


class ElasticacheReplicationGroupEncryptionAtRest(BaseResourceBooleanValueCheck):
    def __init__(self):
        name = "Ensure all data stored in the Elasticache Replication Group  is securely encrypted at rest"
        id = "CKV_AWS_29"
        supported_resources = ['aws_elasticache_replication_group']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "at_rest_encryption_enabled"

check = ElasticacheReplicationGroupEncryptionAtRest()

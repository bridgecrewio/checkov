from checkov.terraform.checks.resource.BaseResourceBooleanValueCheck import BaseResourceBooleanValueCheck
from checkov.terraform.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_check import BaseResourceCheck


class ElasticacheReplicationGroupEncryptionAtTransit(BaseResourceBooleanValueCheck):
    def __init__(self):
        name = "Ensure all data stored in the Elasticache Replication Group  is securely encrypted at transit"
        id = "CKV_AWS_30"
        supported_resources = ['aws_elasticache_replication_group']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "transit_encryption_enabled"


check = ElasticacheReplicationGroupEncryptionAtTransit()

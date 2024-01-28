from checkov.common.models.enums import CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class ElasticacheReplicationGroupEncryptionAtRest(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure all data stored in the ElastiCache Replication Group is securely encrypted at rest"
        id = "CKV_AWS_29"
        supported_resources = ['AWS::ElastiCache::ReplicationGroup']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'Properties/AtRestEncryptionEnabled'


check = ElasticacheReplicationGroupEncryptionAtRest()

from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class DMSReplicationInstancePubliclyAccessible(BaseResourceValueCheck):
    def __init__(self):
        name = "DMS replication instance should not be publicly accessible"
        id = "CKV_AWS_89"
        supported_resources = ['AWS::DMS::ReplicationInstance']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'Properties/PubliclyAccessible'

    def get_expected_value(self):
        return False

check = DMSReplicationInstancePubliclyAccessible()

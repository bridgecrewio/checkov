from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class RDSClusterSnapshotEncrypted(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that RDS database cluster snapshot is encrypted"
        id = "CKV_AWS_146"
        supported_resources = ['aws_db_cluster_snapshot']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'storage_encrypted'


check = RDSClusterSnapshotEncrypted()

from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE


class NeptuneClusterSnapshotEncrypted(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Neptune snapshot is encrypted Customer Managed Key"
        id = "CKV_AWS_280"
        supported_resources = ['aws_neptune_cluster_snapshot']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'kms_key_id'

    def get_expected_value(self):
        return ANY_VALUE


check = NeptuneClusterSnapshotEncrypted()

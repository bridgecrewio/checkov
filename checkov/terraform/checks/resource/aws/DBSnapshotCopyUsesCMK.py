from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class BDSnapshotCopyUsesCMK(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure App Flow connector profile uses CMK"
        id = "CKV_AWS_266"
        supported_resources = ['aws_db_snapshot_copy']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'kms_key_id'

    def get_expected_value(self):
        return ANY_VALUE


check = BDSnapshotCopyUsesCMK()

from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE


class StorageBlockBackupEnabled(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure OCI Block Storage Block Volume has backup enabled"
        id = "CKV_OCI_2"
        supported_resources = ['oci_core_volume']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "backup_policy_id"

    def get_expected_value(self):
        return ANY_VALUE


check = StorageBlockBackupEnabled()

from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE

class ObjectStorageBucketEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure storage bucket is encrypted."
        id = "CKV_YC_3"
        supported_resources = ["yandex_storage_bucket"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "server_side_encryption_configuration/[0]/rule/[0]/apply_server_side_encryption_by_default/[0]/kms_master_key_id"

    def get_expected_value(self):
        return ANY_VALUE
    
check = ObjectStorageBucketEncryption()
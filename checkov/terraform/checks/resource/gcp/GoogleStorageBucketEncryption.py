from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class GoogleStorageBucketEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Google storage bucket have encryption enabled"
        id = "CKV_GCP_5"
        supported_resources = ['google_storage_bucket']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'encryption/[0]/default_kms_key_name'

    def get_expected_values(self):
        return [ANY_VALUE]


check = GoogleStorageBucketEncryption()

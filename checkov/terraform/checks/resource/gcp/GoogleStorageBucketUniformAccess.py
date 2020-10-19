from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class GoogleStorageBucketUniformAccess(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that Cloud Storage buckets have uniform bucket-level access enabled"
        id = "CKV_GCP_29"
        supported_resources = ['google_storage_bucket']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'uniform_bucket_level_access/[0]/bucket_policy_only/[0]'


check = GoogleStorageBucketUniformAccess()

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class GoogleStorageBucketUniformAccess(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that Cloud Storage buckets have uniform bucket-level access enabled"
        id = "CKV_GCP_29"
        supported_resources = ['google_storage_bucket']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'bucket_policy_only' in conf.keys():
            if conf['bucket_policy_only'][0]:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = GoogleStorageBucketUniformAccess()

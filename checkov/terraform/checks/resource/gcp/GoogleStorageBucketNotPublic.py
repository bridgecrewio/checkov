from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class GoogleStorageBucketNotPublic(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that Cloud Storage bucket is not anonymously or publicly accessible"
        id = "CKV_GCP_28"
        supported_resources = ['google_storage_bucket_iam_member', 'google_storage_bucket_iam_binding']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        member_conf = conf.get('member', []) + conf.get('members', [[]])[0]
        if not any(member in member_conf for member in ['allUsers', 'allAuthenticatedUsers']):
            return CheckResult.PASSED
        return CheckResult.FAILED


check = GoogleStorageBucketNotPublic()

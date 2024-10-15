from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class OSSBucketEncryptionCheck(BaseResourceCheck):
    def __init__(self):
        # This is the full description of your check
        description = "Ensures that OSS buckets have server-side encryption enabled."

        # This is the Unique ID for your check
        id = "CKV_ALI_1374"

        # These are the terraform objects supported by this check (ex: aws_iam_policy_document)
        supported_resources = ['alicloud_oss_bucket']

        # Valid CheckCategories are defined in checkov/common/models/enums.py
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=description, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        # Replace this with the custom logic for your check
        if (
                "server_side_encryption_rule" in conf
                and conf["server_side_encryption_rule"]
        ):
            return CheckResult.PASSED

        return CheckResult.FAILED


check = OSSBucketEncryptionCheck()

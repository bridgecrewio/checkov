from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class S3KMSEncryptedByDefault(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that S3 buckets are encrypted with KMS by default"
        id = "CKV_AWS_145"
        supported_resources = ['aws_s3_bucket']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "server_side_encryption_configuration/[0]/rule/[0]/" \
               "apply_server_side_encryption_by_default/[0]/sse_algorithm"

    def get_expected_value(self):
        return 'aws:kms'


check = S3KMSEncryptedByDefault()

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class S3Encryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure all data stored in the S3 bucket is securely encrypted at rest"
        id = "CKV_AWS_19"
        supported_resources = ['aws_s3_bucket']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'server_side_encryption_configuration/[0]/rule/[0]/' \
               'apply_server_side_encryption_by_default/[0]/sse_algorithm'

    def get_expected_value(self):
        return 'AES256'

    def get_expected_values(self):
        return [self.get_expected_value(), 'aws:kms']


check = S3Encryption()

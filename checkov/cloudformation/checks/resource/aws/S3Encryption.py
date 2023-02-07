from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class S3Encryption(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure the S3 bucket has server-side-encryption enabled"
        id = "CKV_AWS_19"
        supported_resources = ['AWS::S3::Bucket']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)
        self.missing_block_result = CheckResult.PASSED  # The default value for this resource is to encrypt

    def get_inspected_key(self):
        return 'Properties/BucketEncryption/ServerSideEncryptionConfiguration/[0]/ServerSideEncryptionByDefault/SSEAlgorithm'

    def get_expected_value(self):
        return 'AES256'

    def get_expected_values(self):
        return [self.get_expected_value(), 'aws:kms']


check = S3Encryption()

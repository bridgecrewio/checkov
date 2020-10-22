from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class S3Versioning(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure the S3 bucket has versioning enabled"
        id = "CKV_AWS_21"
        supported_resources = ['AWS::S3::Bucket']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'Properties/VersioningConfiguration/Status'

    def get_expected_value(self):
        """
        Returns the default expected value, governed by provider best practices
        """

        return 'Enabled'


check = S3Versioning()

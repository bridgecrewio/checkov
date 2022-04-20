from checkov.common.models.enums import CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class CloudfrontDistributionLogging(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Cloudfront distribution has Access Logging enabled"
        id = "CKV_AWS_86"
        supported_resources = ['AWS::CloudFront::Distribution']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'Properties/DistributionConfig/Logging/Bucket'

    def get_expected_value(self):
        return ANY_VALUE


check = CloudfrontDistributionLogging()

from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class CloudfrontDistributionLogging(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure CloudFront distribution has Access Logging enabled"
        id = "CKV_AWS_86"
        supported_resources = ['aws_cloudfront_distribution']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "logging_config/[0]/bucket"

    def get_expected_value(self):
        return ANY_VALUE


check = CloudfrontDistributionLogging()

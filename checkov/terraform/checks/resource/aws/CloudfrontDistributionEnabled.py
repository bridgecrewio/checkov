from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class CloudfrontDistributionEnabled(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Cloudfront distribution is enabled"
        id = "CKV_AWS_216"
        supported_resources = ['aws_cloudfront_distribution']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "enabled"


check = CloudfrontDistributionEnabled()

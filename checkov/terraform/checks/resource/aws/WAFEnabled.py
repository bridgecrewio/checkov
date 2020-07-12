from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class WAFEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "CloudFront Distribution should have WAF enabled"
        id = "CKV_AWS_68"
        supported_resources = ['aws_cloudfront_distribution']
        categories = [CheckCategories.APPLICATION_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'web_acl_id'

    def get_expected_values(self):
        return [ANY_VALUE]


check = WAFEnabled()

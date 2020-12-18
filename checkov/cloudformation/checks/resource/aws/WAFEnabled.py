from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class WAFEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "CloudFront Distribution should have WAF enabled"
        id = "CKV_AWS_68"
        supported_resources = ['AWS::CloudFront::Distribution']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'Properties/DistributionConfig/WebACLId'

    def get_expected_value(self):
        return ANY_VALUE


check = WAFEnabled()

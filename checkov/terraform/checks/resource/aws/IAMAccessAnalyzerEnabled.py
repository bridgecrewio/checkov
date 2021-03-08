from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class IAMAccessAnalyzerEnabled(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure that IAM Access analyzer is enabled"
        id = "CKV2_AWS_3"
        supported_resources = ['aws_accessanalyzer_analyzer']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'resource/[0]/aws_accessanalyzer_analyzer'

    def get_expected_values(self):
        return [ANY_VALUE]


check = IAMAccessAnalyzerEnabled()

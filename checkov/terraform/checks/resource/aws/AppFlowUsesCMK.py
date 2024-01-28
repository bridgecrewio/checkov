from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class AppFlowUsesCMK(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure AppFlow flow uses CMK"
        id = "CKV_AWS_263"
        supported_resources = ['aws_appflow_flow']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'kms_arn'

    def get_expected_value(self):
        return ANY_VALUE


check = AppFlowUsesCMK()

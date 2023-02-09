from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class KendraIndexSSEUsesCMK(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Kendra index Server side encryption uses CMK"
        id = "CKV_AWS_262"
        supported_resources = ['aws_kendra_index']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'server_side_encryption_configuration/[0]/kms_key_id'

    def get_expected_value(self):
        return ANY_VALUE


check = KendraIndexSSEUsesCMK()

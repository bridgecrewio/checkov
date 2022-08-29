from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class ComprehendEntityRecognizerModelUsesCMK(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that Comprehend Entity Recognizer's model is encrypted by KMS using a customer managed Key (CMK)"
        id = "CKV_AWS_267"
        supported_resources = ['aws_comprehend_entity_recognizer']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'model_kms_key_id'

    def get_expected_value(self):
        return ANY_VALUE


check = ComprehendEntityRecognizerModelUsesCMK()

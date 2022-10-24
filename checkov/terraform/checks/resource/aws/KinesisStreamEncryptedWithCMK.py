from checkov.common.models.consts import ANY_VALUE
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class KinesisStreamEncryptedWithCMK(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Kinesis Stream is encrypted by KMS using a customer managed Key (CMK)"
        id = "CKV_AWS_185"
        supported_resources = ['aws_kinesis_stream']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "kms_key_id"

    def get_expected_value(self):
        return ANY_VALUE


check = KinesisStreamEncryptedWithCMK()

from checkov.common.models.consts import ANY_VALUE
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class MQBrokerEncryptedWithCMK(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure MQ broker encrypted by KMS using a customer managed Key (CMK)"
        id = "CKV_AWS_209"
        supported_resources = ['aws_mq_broker']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "encryption_options/[0]/kms_key_id"

    def get_expected_value(self):
        return ANY_VALUE


check = MQBrokerEncryptedWithCMK()

from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class SQSQueueEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure all data stored in the SQS queue is encrypted"
        id = "CKV_AWS_27"
        supported_resources = ['aws_sqs_queue']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'kms_master_key_id'

    def get_expected_value(self):
        return ANY_VALUE


check = SQSQueueEncryption()

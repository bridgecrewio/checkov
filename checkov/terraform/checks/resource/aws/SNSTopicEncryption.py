from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class SNSTopicEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure all data stored in the SNS topic is encrypted"
        id = "CKV_AWS_26"
        supported_resources = ['aws_sns_topic']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'kms_master_key_id'

    def get_expected_values(self):
        return [ANY_VALUE]

    def get_expected_value(self):
        return 'alias/aws/sns'


check = SNSTopicEncryption()

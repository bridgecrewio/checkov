from checkov.common.models.enums import CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class SNSTopicEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure all data stored in the SNS topic is encrypted"
        id = "CKV_AWS_26"
        supported_resources = ['AWS::SNS::Topic']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'Properties/KmsMasterKeyId'

    def get_expected_value(self):
        return ANY_VALUE


check = SNSTopicEncryption()

from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE


class BedrockAgentEncrypted(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Bedrock Agent is encrypted with a CMK"
        id = "CKV_AWS_373"
        supported_resources = ['AWS::Bedrock::Agent']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'Properties/CustomerEncryptionKeyArn'

    def get_expected_value(self):
        return ANY_VALUE


check = BedrockAgentEncrypted()

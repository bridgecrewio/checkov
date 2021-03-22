from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.models.consts import ANY_VALUE


class SecretManagerSecretEncrypted(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure that Secret Manager secret is encrypted using KMS"
        id = "CKV_AWS_152"
        supported_resources = ['aws_secretsmanager_secret']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_expected_value(self):
        return ANY_VALUE

    def get_inspected_key(self):
        return 'kms_key_id'


check = SecretManagerSecretEncrypted()

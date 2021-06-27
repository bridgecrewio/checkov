from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE


class BackupVaultEncrypted(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Backup Vault is encrypted at rest using KMS CMK"
        id = "CKV_AWS_166"
        supported_resources = ['AWS::Backup::BackupVault']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'Properties/EncryptionKeyArn'

    def get_expected_value(self):
        return ANY_VALUE


check = BackupVaultEncrypted()

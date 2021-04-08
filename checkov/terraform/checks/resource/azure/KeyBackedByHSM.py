from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class KeyBackedByHSM(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that key vault key is backed by HSM"
        id = "CKV_AZURE_112"
        supported_resources = ['azurerm_key_vault_key']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'key_type'

    def get_expected_value(self):
        return 'RSA-HSM'

    def get_expected_values(self):
        return [self.get_expected_value(), 'EC-HSM']


check = KeyBackedByHSM()

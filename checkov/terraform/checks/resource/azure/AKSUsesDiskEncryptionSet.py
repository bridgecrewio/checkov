from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class AKSUsesDiskEncryptionSet(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that AKS uses disk encryption set"
        id = "CKV_AZURE_117"
        supported_resources = ['azurerm_kubernetes_cluster']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.FAILED)

    def get_inspected_key(self):
        return "disk_encryption_set_id"

    def get_expected_value(self):
        return ANY_VALUE


check = AKSUsesDiskEncryptionSet()

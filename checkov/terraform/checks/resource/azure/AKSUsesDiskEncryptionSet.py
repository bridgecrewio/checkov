from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class AKSUsesDiskEncryptionSet(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure that AKS uses disk encryption set"
        id = "CKV_AZURE_117"
        supported_resources = ['azurerm_kubernetes_cluster']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_attribute_result=CheckResult.FAILED)

    def get_inspected_key(self):
        return "disk_encryption_set_id"

    def get_forbidden_values(self):
        return ['']


check = AKSUsesDiskEncryptionSet()

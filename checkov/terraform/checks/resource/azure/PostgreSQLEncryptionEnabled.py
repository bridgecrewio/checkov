from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class PostgersSQLEncryptionEnaled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that PostgreSQL server enables infrastructure encryption"
        id = "CKV_AZURE_130"
        supported_resources = ['azurerm_postgresql_server']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'infrastructure_encryption_enabled'



check = PostgersSQLEncryptionEnaled()

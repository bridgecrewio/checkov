from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class MariaDBSSLEnforcementEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure 'Enforce SSL connection' is set to 'ENABLED' for MariaDB servers"
        id = "CKV_AZURE_47"
        supported_resources = ['azurerm_mariadb_server']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'ssl_enforcement_enabled'


check = MariaDBSSLEnforcementEnabled()

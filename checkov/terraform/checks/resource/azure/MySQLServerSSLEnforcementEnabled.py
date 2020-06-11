from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class MySQLServerSSLEnforcementEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure 'Enforce SSL connection' is set to 'ENABLED' for MySQL Database Server"
        id = "CKV_AZURE_28"
        supported_resources = ['azurerm_mysql_server']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'ssl_enforcement_enabled'


check = MySQLServerSSLEnforcementEnabled()

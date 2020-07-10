from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class PostgreSQLServerSSLEnforcementEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure 'Enforce SSL connection' is set to 'ENABLED' for PostgreSQL Database Server"
        id = "CKV_AZURE_29"
        supported_resources = ['azurerm_postgresql_server']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'ssl_enforcement_enabled'


check = PostgreSQLServerSSLEnforcementEnabled()

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class SQLServerAuditingEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that 'Auditing' is set to 'On' for SQL servers"
        id = "CKV_AZURE_23"
        supported_resources = ['azurerm_sql_server', 'azurerm_mssql_server']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'extended_auditing_policy'

    def get_expected_value(self):
        return ANY_VALUE


check = SQLServerAuditingEnabled()

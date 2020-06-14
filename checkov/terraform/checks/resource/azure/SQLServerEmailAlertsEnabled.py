from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class SQLServerEmailAlertsEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that 'Send Alerts To' is enabled for MSSQL servers"
        id = "CKV_AZURE_26"
        supported_resources = ['azurerm_mssql_server_security_alert_policy']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'email_addresses'

    def get_expected_value(self):
        return ANY_VALUE


check = SQLServerEmailAlertsEnabled()

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class SQLServerEmailAlertsToAdminsEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that 'Email service and co-administrators' is 'Enabled'"
        id = "CKV_AZURE_27"
        supported_resources = ['azurerm_mssql_server_security_alert_policy']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'email_account_admins'


check = SQLServerEmailAlertsToAdminsEnabled()

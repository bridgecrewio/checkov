from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class MSSQLServerAuditPolicyLogMonitor(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure default Auditing policy for a SQL Server is configured to capture and retain the activity logs"
        id = "CKV_AZURE_156"
        supported_resources = ['azurerm_mssql_database_extended_auditing_policy']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.FAILED)

    def get_inspected_key(self):
        return "log_monitoring_enabled"


check = MSSQLServerAuditPolicyLogMonitor()

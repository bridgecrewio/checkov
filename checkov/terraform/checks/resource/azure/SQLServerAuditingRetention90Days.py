from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_int
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class SQLServerAuditingRetention90Days(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that 'Auditing' Retention is 'greater than 90 days' for SQL servers"
        id = "CKV_AZURE_24"
        supported_resources = ['azurerm_sql_server', 'azurerm_mssql_server']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'extended_auditing_policy' in conf:
            policy = conf['extended_auditing_policy'][0]
            if not isinstance(policy, dict):
                self.evaluated_keys = ['extended_auditing_policy']
                return CheckResult.UNKNOWN
            retention = force_int(conf['extended_auditing_policy'][0]['retention_in_days'][0])
            self.evaluated_keys = ['extended_auditing_policy/[0]/retention_in_days']
            if retention and retention >= 90:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = SQLServerAuditingRetention90Days()

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_int
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck
from typing import List


class SQLServerAuditPolicyRetentionPeriod(BaseResourceCheck):
    def __init__(self):
        name = "Specifies a retention period of less than 90 days."
        id = "CKV_AZURE_46"
        supported_resources = ['azurerm_mssql_database_extended_auditing_policy']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'retention_in_days' in conf:
            retention = force_int(conf['retention_in_days'][0])
            if retention:
                if retention < 90:
                    return CheckResult.FAILED
                else:
                    return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ['retention_in_days']


check = SQLServerAuditPolicyRetentionPeriod()

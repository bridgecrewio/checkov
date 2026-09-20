from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class SQLServerEmailAlertsToAdminsEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that 'Email service and co-administrators' is 'Enabled' for MSSQL servers"
        id = "CKV_AZURE_27"
        supported_resources = ['azurerm_mssql_server_security_alert_policy']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        # Prefer the renamed attribute while retaining support for older providers.
        if 'email_account_admins_enabled' in conf:
            self.evaluated_keys = ['email_account_admins_enabled']
        else:
            self.evaluated_keys = ['email_account_admins']
        return super().scan_resource_conf(conf)

    def get_inspected_key(self) -> str:
        return self.evaluated_keys[0] if self.evaluated_keys else 'email_account_admins'


check = SQLServerEmailAlertsToAdminsEnabled()

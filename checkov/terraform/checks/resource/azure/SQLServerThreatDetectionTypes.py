from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class SQLServerThreatDetectionTypes(BaseResourceCheck):
    def __init__(self):
        name = " Ensure that 'Threat Detection types' is set to 'All'"
        id = "CKV_AZURE_25"
        supported_resources = ['azurerm_mssql_server_security_alert_policy']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'disabled_alerts' in conf and any(conf['disabled_alerts'][0]):
            return CheckResult.FAILED
        return CheckResult.PASSED


check = SQLServerThreatDetectionTypes()

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class SQLDatabaseThreatDetectionEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that Threat Detection is enabled for SQL Database"
        id = "CKV_AZURE_101"
        supported_resources = ['azurerm_sql_database']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'threat_detection_policy' in conf:
            policy = conf['threat_detection_policy'][0]
            if 'state' in policy and policy['state'][0].upper() == 'ENABLED':
                return CheckResult.PASSED
        return CheckResult.FAILED


check = SQLDatabaseThreatDetectionEnabled()

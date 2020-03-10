from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class GoogleCloudSqlBackupConfiguration(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all Cloud SQL database instance have backup configuration enabled"
        id = "CKV_GCP_14"
        supported_resources = ['google_sql_database_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'settings' in conf and 'backup_configuration' in conf['settings'][0]:
            if conf['settings'][0]['backup_configuration'][0]['enabled']:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = GoogleCloudSqlBackupConfiguration()

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class GoogleCloudSqlBackupConfiguration(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all Cloud SQL database instance have backup configuration enabled"
        id = "CKV_GCP_14"
        supported_resources = ['google_sql_database_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'master_instance_name' in conf:
           return CheckResult.PASSED
        
        if 'settings' in conf:
            settings = conf["settings"][0]
            if isinstance(settings, dict) and 'backup_configuration' in settings:
                backup_configuration = settings["backup_configuration"][0]
                if backup_configuration.get("enabled", None) == [True]:
                    return CheckResult.PASSED

                return CheckResult.FAILED
            return CheckResult.FAILED
        return CheckResult.FAILED

check = GoogleCloudSqlBackupConfiguration()

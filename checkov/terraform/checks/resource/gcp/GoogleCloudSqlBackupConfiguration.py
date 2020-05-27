from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class GoogleCloudSqlBackupConfiguration(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure all Cloud SQL database instance have backup configuration enabled"
        id = "CKV_GCP_14"
        supported_resources = ['google_sql_database_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'settings/[0]/backup_configuration/[0]/enabled'


check = GoogleCloudSqlBackupConfiguration()

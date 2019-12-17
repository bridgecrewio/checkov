from checkov.terraform.checks.resource.base_check import BaseResourceCheck
from checkov.terraform.models.enums import CheckResult, CheckCategories


class GoogleCloudSqlDatabaseRequireSsl(BaseResourceCheck):
    def __init__(self):
        name = "Ensure all Cloud SQL database instance requires all incoming connections to use SSL"
        id = "CKV_GCP_6"
        supported_resources = ['google_sql_database_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for google_sql_database_instance which do not enforce SSL connections:
        :param conf: google_sql_database_instance configuration
        :return: <CheckResult>
        """
        if 'settings' in conf and 'ip_configuration' in conf['settings'][0]:
            if 'require_ssl' in conf['settings'][0]['ip_configuration'][0].keys():
                if conf['settings'][0]['ip_configuration'][0]['require_ssl'][0] == "True":
                    return CheckResult.PASSED
        return CheckResult.FAILED


check = GoogleCloudSqlDatabaseRequireSsl()

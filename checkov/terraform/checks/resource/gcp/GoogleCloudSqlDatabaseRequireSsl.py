from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class GoogleCloudSqlDatabaseRequireSsl(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure all Cloud SQL database instance requires all incoming connections to use SSL"
        id = "CKV_GCP_6"
        supported_resources = ['google_sql_database_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        """
        Looks for google_sql_database_instance which do not enforce SSL connections:
        :param
        conf: google_sql_database_instance
        configuration
        :return: < CheckResult >
        """
        return 'settings/[0]/ip_configuration/[0]/require_ssl/[0]'

check = GoogleCloudSqlDatabaseRequireSsl()

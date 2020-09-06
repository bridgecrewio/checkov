from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class GoogleCloudPostgreSqlLogConnection(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure PostgreSQL database 'log_connections' flag is set to 'on'"
        check_id = "CKV_GCP_52"
        supported_resources = ['google_sql_database_instance']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=check_id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for google_sql_database_instance which allows log connections on PostgreSQL DBs::
            :param
            conf: google_sql_database_instance
            configuration
            :return: < CheckResult >
        """
        if 'database_version' in conf.keys():
            key = conf['database_version'][0]
            if key == 'POSTGRES_9_6' or key == 'POSTGRES_10' or key == 'POSTGRES_11' or key == 'POSTGRES_12':
                if 'settings' in conf.keys():
                    for attribute in conf['settings'][0]:
                        if attribute=='database_flags':
                            for flag in conf['settings'][0]['database_flags']:
                                if (flag['name'][0]=='log_connections') and (flag['value'][0]=='off'):
                                    return CheckResult.FAILED
        return CheckResult.PASSED

    def get_inspected_key(self):
        return 'settings/[0]/database_flags/[0]/log_connections'

    def get_expected_value(self):
        return "on"

check = GoogleCloudPostgreSqlLogConnection()

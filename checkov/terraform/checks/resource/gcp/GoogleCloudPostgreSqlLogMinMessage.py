from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

class GoogleCloudPostgreSqlLogMinMessage(BaseResourceCheck):
    def __init__(self):
                name = "Ensure PostgreSQL database 'log_min_messages' flag is set to a valid value"
                check_id = "CKV_GCP_55"
                supported_resources = ['google_sql_database_instance']
                categories = [CheckCategories.LOGGING]
                super().__init__(name=name, id=check_id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
                """
                    Looks for google_sql_database_instance which has valid value in log_min_messages flag on PostgreSQL DBs::
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
                                if attribute == 'database_flags':
                                    for flag in conf['settings'][0]['database_flags']:
                                        if (flag['name'][0] == 'log_min_messages'):
                                            key_logmin=flag['value'][0]
                                            if (key_logmin != 'fatal' and key_logmin != 'panic' and key_logmin != 'log' and key_logmin != 'error' and key_logmin != 'warning' and key_logmin != 'notice'
                                                    and key_logmin != 'info' and key_logmin != 'debug1' and key_logmin != 'debug2' and key_logmin != 'debug3' and key_logmin != 'debug4' and key_logmin != 'debug5'):
                                                return CheckResult.FAILED
                return CheckResult.PASSED


check = GoogleCloudPostgreSqlLogMinMessage()

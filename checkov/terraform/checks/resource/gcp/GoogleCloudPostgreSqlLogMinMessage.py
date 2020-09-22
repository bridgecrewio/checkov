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
            if 'POSTGRES' in key:
                if 'settings' in conf.keys():
                    for attribute in conf['settings'][0]:
                        if attribute == 'database_flags':
                            flags = conf['settings'][0]['database_flags']
                            if isinstance(flags[0], list): #treating use cases of the following database_flags parsing (list of list of dictionaries with strings):'database_flags': [[{'name': '<key>', 'value': '<value>'}, {'name': '<key>', 'value': '<value>'}]]
                                flags = conf['settings'][0]['database_flags'][0]
                                for flag in flags:
                                    if (flag['name'] == 'log_min_messages'):
                                        key_logmin = flag['value']
                                        logmin_list = ['fatal', 'panic', 'log', 'error', 'warning', 'notice',
                                                       'info', 'debug1', 'debug2', 'debug3', 'debug4', 'debug5']
                                        if key_logmin not in logmin_list:
                                            return CheckResult.FAILED
                            else: #treating use cases of the following database_flags parsing (list of dictionaries with arrays): 'database_flags': [{'name': ['<key>'], 'value': ['<value>']},{'name': ['<key>'], 'value': ['<value>']}]
                                for flag in flags:
                                    if (flag['name'][0] == 'log_min_messages'):
                                        key_logmin = flag['value'][0]
                                        logmin_list = ['fatal', 'panic', 'log', 'error', 'warning', 'notice',
                                                       'info', 'debug1', 'debug2', 'debug3', 'debug4', 'debug5']
                                        if key_logmin not in logmin_list:
                                            return CheckResult.FAILED
        return CheckResult.PASSED


check = GoogleCloudPostgreSqlLogMinMessage()

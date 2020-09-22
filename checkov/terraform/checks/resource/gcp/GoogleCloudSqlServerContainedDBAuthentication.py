from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class GoogleCloudSqlServerContainedDBAuthentication(BaseResourceCheck):
    def __init__(self):
        name = "Ensure SQL database 'contained database authentication' flag is set to 'off'"
        check_id = "CKV_GCP_59"
        supported_resources = ['google_sql_database_instance']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=check_id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for google_sql_database_instance which prevents containes DB authentication on SQL DBs::
            :param
            conf: google_sql_database_instance
            configuration
            :return: < CheckResult >
        """
        if 'database_version' in conf.keys():
            key = conf['database_version'][0]
            if 'SQLSERVER' in key:
                if 'settings' in conf.keys():
                    for attribute in conf['settings'][0]:
                        if attribute == 'database_flags':
                            flags = conf['settings'][0]['database_flags']
                            if isinstance(flags[0], list): #treating use cases of the following database_flags parsing (list of list of dictionaries with strings):'database_flags': [[{'name': '<key>', 'value': '<value>'}, {'name': '<key>', 'value': '<value>'}]]
                                flags = conf['settings'][0]['database_flags'][0]
                                for flag in flags:
                                    if (flag['name'] == 'contained database authentication') and (
                                            flag['value'] == 'on'):
                                        return CheckResult.FAILED
                            else: #treating use cases of the following database_flags parsing (list of dictionaries with arrays): 'database_flags': [{'name': ['<key>'], 'value': ['<value>']},{'name': ['<key>'], 'value': ['<value>']}]
                                for flag in flags:
                                    if (flag['name'][0] == 'contained database authentication') and (
                                            flag['value'][0] == 'on'):
                                        return CheckResult.FAILED
        return CheckResult.PASSED


check = GoogleCloudSqlServerContainedDBAuthentication()

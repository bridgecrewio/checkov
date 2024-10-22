from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class GoogleCloudPostgreSqlLogDisconnection(BaseResourceCheck):
    def __init__(self):
        name = "Ensure PostgreSQL database 'log_disconnections' flag is set to 'on'"
        check_id = "CKV_GCP_53"
        supported_resources = ['google_sql_database_instance']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=check_id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for google_sql_database_instance which allows log disconnections on PostgreSQL DBs::
            :param
            conf: google_sql_database_instance
            configuration
            :return: < CheckResult >
        """
        if 'database_version' in conf.keys() and isinstance(conf['database_version'][0], str) and 'POSTGRES' in conf['database_version'][0]:
            if 'settings' in conf.keys():
                self.evaluated_keys = ['database_version/[0]/POSTGRES', 'settings']
                flags = conf['settings'][0].get('database_flags')
                if flags:
                    evaluated_keys_prefix = 'settings/[0]/database_flags'
                    if isinstance(flags[0], list):
                        # treating use cases of the following database_flags parsing
                        # (list of list of dictionaries with strings):'database_flags':
                        # [[{'name': '<key>', 'value': '<value>'}, {'name': '<key>', 'value': '<value>'}]]
                        flags = flags[0]
                        evaluated_keys_prefix += '/[0]'
                    else:
                        # treating use cases of the following database_flags parsing
                        # (list of dictionaries with arrays): 'database_flags':
                        # [{'name': ['<key>'], 'value': ['<value>']},{'name': ['<key>'], 'value': ['<value>']}]
                        flags = [{key: flag[key][0] for key in flag if key in ['name', 'value']} for flag in flags]
                    for flag in flags:
                        if (isinstance(flag, dict) and flag['name'] == 'log_disconnections') and (flag['value'] == 'on'):  # Must be explicitly set for check to pass
                            self.evaluated_keys = ['database_version/[0]/POSTGRES',
                                                   f'{evaluated_keys_prefix}/[{flags.index(flag)}]/name',
                                                   f'{evaluated_keys_prefix}/[{flags.index(flag)}]/value']
                            return CheckResult.PASSED
                    self.evaluated_keys = ['database_version/[0]/POSTGRES', 'settings/[0]/database_flags']

            return CheckResult.FAILED
        return CheckResult.UNKNOWN


check = GoogleCloudPostgreSqlLogDisconnection()

from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class AbsGooglePostgresqlDatabaseFlags(BaseResourceCheck):
    def __init__(self, name, id, categories, supported_resources, flag_name, flag_values):
        super().__init__(name, id, categories, supported_resources)
        self.flag_name = flag_name
        self.flag_values = flag_values

    def scan_resource_conf(self, conf):
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
                        if isinstance(flag, dict) and flag['name'] == self.flag_name and flag['value'] in self.flag_values:
                            self.evaluated_keys = ['database_version/[0]/POSTGRES',
                                                   f'{evaluated_keys_prefix}/[{flags.index(flag)}]/name',
                                                   f'{evaluated_keys_prefix}/[{flags.index(flag)}]/value']
                            return CheckResult.PASSED
                    self.evaluated_keys = ['database_version/[0]/POSTGRES', 'settings/[0]/database_flags']
            return CheckResult.FAILED
        return CheckResult.UNKNOWN

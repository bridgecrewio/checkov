from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

ALLOWED_SSL_MODES = ["TRUSTED_CLIENT_CERTIFICATE_REQUIRED"]


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
        :param
        conf: google_sql_database_instance
        configuration
        :return: < CheckResult >
        """

        if 'settings' in conf.keys() and 'ip_configuration' in conf['settings'][0]:
            ipconfiguration = conf['settings'][0]['ip_configuration'][0]

            if 'ssl_mode' in ipconfiguration:
                ssl_mode = ipconfiguration['ssl_mode']
                ssl_mode = ssl_mode[0] if isinstance(ssl_mode, list) else ssl_mode

                if ssl_mode in ALLOWED_SSL_MODES:
                    return CheckResult.PASSED

            elif 'require_ssl' in ipconfiguration:

                require_ssl = ipconfiguration['require_ssl']
                require_ssl = require_ssl[0] if isinstance(require_ssl, list) else require_ssl

                if require_ssl:
                    return CheckResult.PASSED

        return CheckResult.FAILED

    def get_inspected_keys(self):
        return ['settings/[0]/ip_configuration/[0]/ssl_mode/[0]', 'settings/[0]/ip_configuration/[0]/require_ssl/[0]']


check = GoogleCloudSqlDatabaseRequireSsl()

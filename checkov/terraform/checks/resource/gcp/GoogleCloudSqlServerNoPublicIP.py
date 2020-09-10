from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class GoogleCloudSqlServerNoPublicIP(BaseResourceCheck):
    def __init__(self):
        name = "Ensure SQL database do not have public IP"
        check_id = "CKV_GCP_60"
        supported_resources = ['google_sql_database_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=check_id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for google_sql_database_instance which have no public IPs on SQL DBs::
            :param
            conf: google_sql_database_instance
            configuration
            :return: < CheckResult >
        """
        if 'database_version' in conf.keys():
            key = conf['database_version'][0]
            if 'SQLSERVER' in key:
                if 'settings' in conf.keys():
                    if 'ip_configuration' in conf['settings'][0]:
                        if 'ipv4_enabled' in conf['settings'][0]['ip_configuration'][0]:
                            if conf['settings'][0]['ip_configuration'][0]['ipv4_enabled'][0] != 'false':
                                return CheckResult.FAILED
        return CheckResult.PASSED


check = GoogleCloudSqlServerNoPublicIP()

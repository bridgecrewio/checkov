from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class GoogleCloudSqlServerNoPublicIP(BaseResourceValueCheck):
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
            if key == 'SQLSERVER_2017_STANDARD' or key == 'SQLSERVER_2017_ENTERPRISE' or key == 'SQLSERVER_2017_EXPRESS' or key == 'SQLSERVER_2017_WEB':
                if 'settings' in conf.keys():
                    if 'ip_configuration' in conf['settings'][0]:
                        if 'ipv4_enabled' in conf['settings'][0]['ip_configuration'][0]:
                            if conf['settings'][0]['ip_configuration'][0]['ipv4_enabled'][0] != 'false':
                                return CheckResult.FAILED
        return CheckResult.PASSED

    def get_inspected_key(self):
        return 'settings/[0]/ip_configuration/[0]/ipv4_enabled'

    def get_expected_value(self):
        return "false"


check=GoogleCloudSqlServerNoPublicIP()

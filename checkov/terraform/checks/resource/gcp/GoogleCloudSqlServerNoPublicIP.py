from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class GoogleCloudSqlServerNoPublicIP(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Cloud SQL database does not have public IP"
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

        if 'settings' in conf.keys() and 'ip_configuration' in conf['settings'][0] and \
                'ipv4_enabled' in conf['settings'][0]['ip_configuration'][0]:
            ipconfiguration = conf['settings'][0]['ip_configuration'][0]
            if ipconfiguration['ipv4_enabled'][0]:
                self.evaluated_keys = ['database_version/[0]/SQLSERVER',
                                       'settings/[0]/ip_configuration/[0]/ipv4_enabled']
                return CheckResult.FAILED
        return CheckResult.PASSED


check = GoogleCloudSqlServerNoPublicIP()

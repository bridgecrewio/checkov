from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories

class GoogleCloudSqlDatabasePublicallyAccessible(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that Cloud SQL database Instances are not open to the world"
        id = "CKV_GCP_11"
        supported_resources = ['google_sql_database_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for google_sql_database_instance which is open to the world:
        :param conf: google_sql_database_instance configuration
        :return: <CheckResult>
        """
        authorized_networks_count = 0
        authorized_networks_passed = 0
        if 'settings' in conf and 'ip_configuration' in conf['settings'][0]:
            if 'authorized_networks' in conf['settings'][0]['ip_configuration'][0].keys():
                authorized_networks_count = len(conf['settings'][0]['ip_configuration'][0]['authorized_networks'][0])
                for authorized_network in conf['settings'][0]['ip_configuration'][0]['authorized_networks'][0]:
                    if isinstance(authorized_network, str):
                        return CheckResult.UNKNOWN
                    if 'value' in authorized_network.keys():
                        if "/0" not in authorized_network['value']:
                            authorized_networks_passed += 1

        if authorized_networks_passed == authorized_networks_count:
            return CheckResult.PASSED
        else: 
            return CheckResult.FAILED


check = GoogleCloudSqlDatabasePublicallyAccessible()

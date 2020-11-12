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

        if 'settings' in conf and 'ip_configuration' in conf['settings'][0]:
            ip_config = conf['settings'][0]['ip_configuration'][0]
            if 'authorized_networks' in ip_config:
                auth_networks = ip_config['authorized_networks'][0]
                if type(auth_networks) != list:  # handle possible legacy case
                    auth_networks = [auth_networks]
                for network in auth_networks:
                    if 'value' in network:
                        val = network['value']
                        if type(val) == list:  # handle possible parsing discrepancies
                            val = val[0]
                        if val.endswith('/0'):
                            return CheckResult.FAILED
            if 'dynamic' in ip_config:
                dynamic = ip_config['dynamic']
                for dynamic_block in dynamic:
                    if 'authorized_networks' in dynamic_block:
                        auth_network = dynamic_block['authorized_networks']
                        if 'content' in auth_network:
                            content = auth_network['content'][0]
                            if 'value' in content and content['value'][0].endswith('/0'):
                                return CheckResult.FAILED

        return CheckResult.PASSED


check = GoogleCloudSqlDatabasePublicallyAccessible()

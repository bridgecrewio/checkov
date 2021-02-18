from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class MariaDBPublicAccessDisabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure 'public network access enabled' is set to 'False' for MariaDB servers"
        id = "CKV_AZURE_48"
        supported_resources = ['azurerm_mariadb_server']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        #Whether or not public network access is allowed for this server. Defaults to true. Which is not optimal
        if 'public_network_access_enabled' not in conf: 
            return CheckResult.FAILED
        else:
            if  conf['public_network_access_enabled'][0]:
                return CheckResult.FAILED
            else:
                return CheckResult.PASSED

check = MariaDBPublicAccessDisabled()

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class MySQLServerHasPublicAccessDisabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that MySQL server disables public network access"
        id = "CKV_AZURE_90"
        supported_resources = ['azurerm_mysql_server']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'public_network_access_enabled'

    def scan_resource_conf(self, conf):
        public_access = conf.get('public_network_access_enabled', [True])
        if public_access[0]:
            return CheckResult.FAILED
        return CheckResult.PASSED


check = MySQLServerHasPublicAccessDisabled()

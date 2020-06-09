from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class NetworkWatcherFlowLogEnabled(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that Network Security Group Flow Log retention period is 'greater than 90 days'"
        id = "CKV_AZURE_12"
        supported_resources = ['azurerm_network_watcher_flow_log']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'enabled' in conf and conf['enabled'][0]:
            retention_block = conf['retention_policy'][0]
            if retention_block['enabled'][0] and int(retention_block['days'][0]) >= 90:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = NetworkWatcherFlowLogEnabled()

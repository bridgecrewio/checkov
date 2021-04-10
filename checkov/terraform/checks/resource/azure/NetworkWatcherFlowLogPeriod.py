from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_int
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class NetworkWatcherFlowLogPeriod(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that Network Security Group Flow Log retention period is 'greater than 90 days'"
        id = "CKV_AZURE_12"
        supported_resources = ['azurerm_network_watcher_flow_log']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'enabled' in conf and conf['enabled'][0]:
            retention_block = conf['retention_policy'][0]
            if retention_block['enabled'][0]:
                retention_in_days = force_int(retention_block['days'][0])
                if retention_in_days is not None and (retention_in_days == 0 or retention_in_days >= 90):
                    return CheckResult.PASSED
        return CheckResult.FAILED


check = NetworkWatcherFlowLogPeriod()

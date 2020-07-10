from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_int

# https://docs.microsoft.com/en-us/azure/templates/microsoft.network/2020-04-01/networkwatchers/flowlogs

class NetworkWatcherFlowLogPeriod(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that Network Security Group Flow Log retention period is 'greater than 90 days'"
        id = "CKV_AZURE_12"
        supported_resources = ['Microsoft.Network/networkWatchers/flowLogs',
                               'Microsoft.Network/networkWatchers/FlowLogs',
                               'Microsoft.Network/networkWatchers/flowLogs/',
                               'Microsoft.Network/networkWatchers/FlowLogs/']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if "properties" in conf:
            if "enabled" in conf["properties"]:
                if str(conf["properties"]["enabled"]).lower() == "true":
                    if "retentionPolicy" in conf["properties"]:
                        if "enabled" in conf["properties"]["retentionPolicy"]:
                            if str(conf["properties"]["retentionPolicy"]["enabled"]).lower() == "true":
                                if "days" in conf["properties"]["retentionPolicy"]:
                                    if force_int(conf["properties"]["retentionPolicy"]["days"]) >= 90:
                                        return CheckResult.PASSED
        return CheckResult.FAILED

check = NetworkWatcherFlowLogPeriod()

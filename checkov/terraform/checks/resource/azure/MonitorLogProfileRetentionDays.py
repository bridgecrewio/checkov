from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck
from checkov.common.util.type_forcers import force_int


class MonitorLogProfileRetentionDays(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that Activity Log Retention is set 365 days or greater"
        id = "CKV_AZURE_37"
        supported_resources = ['azurerm_monitor_log_profile']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if not conf.get('retention_policy'):
            return CheckResult.FAILED
        if conf['retention_policy'][0]['enabled'][0]:
            if 'days' in conf['retention_policy'][0] and force_int(conf['retention_policy'][0]['days'][0]) >= 365:
                return CheckResult.PASSED
        elif not conf['retention_policy'][0]['enabled'][0]:
            if 'days' in conf['retention_policy'][0]:
                if force_int(conf['retention_policy'][0]['days']) == 0:
                    return CheckResult.PASSED
            return CheckResult.PASSED
        return CheckResult.FAILED


check = MonitorLogProfileRetentionDays()

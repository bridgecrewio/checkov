from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class MonitorLogProfileRetentionDays(BaseResourceCheck):
    def __init__(self):
        name = "Ensure audit profile captures all the activities"
        id = "CKV_AZURE_38"
        supported_resources = ['azurerm_monitor_log_profile']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        categories = ['Write', 'Delete', 'Action']
        res_categories = conf.get('categories')
        if isinstance(res_categories, list) and res_categories and \
                all(category in conf['categories'][0] for category in categories):
            return CheckResult.PASSED
        return CheckResult.FAILED


check = MonitorLogProfileRetentionDays()

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import (
    BaseResourceCheck, CheckResult)


class CVMDisableMonitorService(BaseResourceCheck):
    def __init__(self):
        name = "Ensure CVM monitor service is enabled"
        id = "CKV_TC_3"
        supported_resources = ['tencentcloud_instance']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict) -> CheckResult:
        if conf.get("disable_monitor_service") and conf["disable_monitor_service"][0]:
            return CheckResult.FAILED
        return CheckResult.PASSED

check = CVMDisableMonitorService()

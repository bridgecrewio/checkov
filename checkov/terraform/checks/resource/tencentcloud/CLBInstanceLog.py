from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import \
    BaseResourceCheck


class CLBInstanceLog(BaseResourceCheck):
    def __init__(self):
        name = "Ensure CLB config log_set_id and log_topic_id"
        id = "CKV_TC_11"
        supported_resources = ['tencentcloud_clb_instance']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if conf.get("log_set_id") is None or conf.get("log_topic_id") is None:
            return CheckResult.FAILED
        return CheckResult.PASSED


check = CLBInstanceLog()

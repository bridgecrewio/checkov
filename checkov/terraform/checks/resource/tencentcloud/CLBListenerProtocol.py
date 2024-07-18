from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import \
    BaseResourceCheck


class CLBListenerProtocol(BaseResourceCheck):
    def __init__(self):
        name = "Check CLB listren protocol"
        id = "CKV_TC_12"
        supported_resources = ['tencentcloud_clb_listener']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if conf.get("protocol") and conf.get("protocol")[0] in ["TCP", "UDP", "HTTP"]:
            return CheckResult.FAILED
        return CheckResult.PASSED


check = CLBListenerProtocol()

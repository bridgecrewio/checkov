from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import \
    BaseResourceCheck


class VPCFlowLogConfigEnable(BaseResourceCheck):
    def __init__(self):
        name = "Ensure VPC flow log disabled"
        id = "CKV_TC_14"
        supported_resources = ['tencentcloud_vpc_flow_log_config']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict) -> CheckResult:
        if conf.get("enable") and not conf["enable"][0]:
            return CheckResult.FAILED
        return CheckResult.PASSED

check = VPCFlowLogConfigEnable()

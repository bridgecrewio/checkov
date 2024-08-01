from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import \
    BaseResourceCheck


class CVMUseDefaultVPC(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Tencent Cloud CVM instances do not use the default VPC"
        id = "CKV_TC_5"
        supported_resources = ['tencentcloud_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if conf.get("vpc_id") and ".default." in conf["vpc_id"][0]:
            return CheckResult.FAILED
        if conf.get("subnet_id") and ".default." in conf["subnet_id"][0]:
            return CheckResult.FAILED
        return CheckResult.PASSED


check = CVMUseDefaultVPC()

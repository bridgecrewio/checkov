from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import \
    BaseResourceCheck


class CVMUseDefaultSecurityGroup(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Tencent Cloud CVM instances do not use the default security group "
        id = "CKV_TC_4"
        supported_resources = ['tencentcloud_instance']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict) -> CheckResult:
        if conf.get("orderly_security_groups"):
            for osg in conf["orderly_security_groups"][0]:
                if ".default." in osg:
                    self.evaluated_keys = ["orderly_security_groups"]
                    return CheckResult.FAILED

        if conf.get("security_groups"):
            for sg in conf["security_groups"][0]:
                if ".default." in sg:
                    self.evaluated_keys = ["security_groups"]
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = CVMUseDefaultSecurityGroup()

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import (
    BaseResourceCheck, CheckResult)


class CVMUserData(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Tencent Cloud CVM user data does not contain sensitive information"
        id = "CKV_TC_13"
        supported_resources = ['tencentcloud_instance']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict) -> CheckResult:
        if conf.get("user_data_raw") and ("TENCENTCLOUD_SECRET_ID" in conf["user_data_raw"][0] or "TENCENTCLOUD_SECRET_KEY" in conf["user_data_raw"][0]):
            self.evaluated_keys = ["user_data_raw"]
            return CheckResult.FAILED
        if conf.get("user_data") and ("TENCENTCLOUD_SECRET_ID" in conf["user_data"][0] or "TENCENTCLOUD_SECRET_KEY" in conf["user_data"][0]):
            self.evaluated_keys = ["user_data"]
            return CheckResult.FAILED
        return CheckResult.PASSED


check = CVMUserData()

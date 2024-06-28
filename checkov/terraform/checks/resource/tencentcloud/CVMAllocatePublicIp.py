from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import (
    BaseResourceCheck, CheckResult)


class CVMAllocatePublicIp(BaseResourceCheck):
    def __init__(self):
        name = "Ensure CVM instance should not allocate public IP"
        id = "CKV_TC_2"
        supported_resources = ['tencentcloud_instance']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict) -> CheckResult:
        if conf.get("allocate_public_ip") and conf["allocate_public_ip"][0]:
            return CheckResult.FAILED
        return CheckResult.PASSED

check = CVMAllocatePublicIp()

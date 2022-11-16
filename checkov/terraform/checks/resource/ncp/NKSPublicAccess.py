from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class NKSPublicAccess(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Naver Kubernetes Service public endpoint disabled"
        id = "CKV_NCP_19"
        supported_resources = ("ncloud_nks_cluster",)
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if "public_network" in conf.keys():
            if conf.get("public_network") == [False]:
                return CheckResult.PASSED
            else:
                return CheckResult.FAILED
        else:
            return CheckResult.PASSED


check = NKSPublicAccess()

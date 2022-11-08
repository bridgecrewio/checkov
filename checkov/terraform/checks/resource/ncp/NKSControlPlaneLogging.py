from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class NKSControlPlaneLogging(BaseResourceCheck):
    def __init__(self):
        name = "Ensure NKS control plane logging enabled for all log types"
        id = "CKV_NCP_21"
        supported_resources = ('ncloud_nks_cluster',)
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if "log" in conf.keys() and conf["log"][0] is not None \
                and conf["log"][0]["audit"][0] is True:
            return CheckResult.PASSED
        return CheckResult.FAILED


check = NKSControlPlaneLogging()

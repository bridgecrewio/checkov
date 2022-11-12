from __future__ import annotations

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class LBNetworkPrivate(BaseResourceCheck):

    def __init__(self):
        name = "Ensure LB isn't exposed to the internet"
        id = "CKV_NCP_16"
        supported_resources = ("ncloud_lb",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if "network_type" in conf.keys():
            network_type = conf["network_type"]
            if network_type in (["PRIVATE"],):
                return CheckResult.PASSED
        return CheckResult.FAILED


check = LBNetworkPrivate()

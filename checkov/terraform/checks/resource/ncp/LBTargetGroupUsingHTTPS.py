from __future__ import annotations

from typing import List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class LBTargetGroupUsingHTTPS(BaseResourceCheck):

    def __init__(self):
        name = "Ensure Load Balancer Target Group is not using HTTP"
        id = "CKV_NCP_15"
        supported_resources = ("ncloud_lb_target_group",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if "protocol" in conf.keys():
            if conf.get("protocol") != ['HTTP']:
                return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ["protocol"]


check = LBTargetGroupUsingHTTPS()

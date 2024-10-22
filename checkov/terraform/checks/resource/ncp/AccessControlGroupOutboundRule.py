from __future__ import annotations

from typing import Any

from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class AccessControlGroupOutboundRule(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure no security group rules allow outbound traffic to 0.0.0.0/0"
        id = "CKV_NCP_3"
        supported_resources = ("ncloud_access_control_group_rule",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        for outbound in conf.get("outbound", []):
            ip = outbound.get("ip_block")
            if ip == ["0.0.0.0/0"] or ip == ["::/0"]:
                return CheckResult.FAILED
        return CheckResult.PASSED


check = AccessControlGroupOutboundRule()

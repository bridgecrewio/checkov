from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.terraform.plan_parser import TF_PLAN_RESOURCE_CHANGE_ACTIONS, TF_PLAN_RESOURCE_CHANGE_KEYS


class SecurityGroupRuleProtocolChanged(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure security group rule protocol is not being changed"
        id = "CUSTOM_CHANGE_1"
        supported_resources = ("aws_security_group_rule",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        actions = conf.get(TF_PLAN_RESOURCE_CHANGE_ACTIONS)
        if isinstance(actions, list) and "update" in actions:
            if "protocol" in conf.get(TF_PLAN_RESOURCE_CHANGE_KEYS):
                self.details.append("some great details")
                return CheckResult.FAILED
        return CheckResult.PASSED


check = SecurityGroupRuleProtocolChanged()

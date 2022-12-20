from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.terraform.plan_parser import TF_PLAN_RESOURCE_CHANGE_ACTIONS


class KmsKeyNotDeleted(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Secret is not deleted"
        id = "CUSTOM_DELETE_1"
        supported_resources = ("aws_secretsmanager_secret",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        actions = conf.get(TF_PLAN_RESOURCE_CHANGE_ACTIONS)
        if isinstance(actions, list) and "delete" in actions:
            self.details.append("some great details")
            return CheckResult.FAILED
        return CheckResult.PASSED


scanner = KmsKeyNotDeleted()

from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class IAMRoleMaxSessionDuration(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure IAM role max session duration does not exceed 1 hour"
        id = "CKV_AWS_395"
        supported_resources = ("aws_iam_role",)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if "max_session_duration" in conf:
            value = conf["max_session_duration"][0]
            if isinstance(value, int):
                if value <= 3600:
                    return CheckResult.PASSED
                return CheckResult.FAILED
            # value is a variable reference or an expression checkov could not
            # resolve at scan time -> cannot evaluate
            return CheckResult.UNKNOWN
        # attribute not set -> Terraform/AWS default of 3600 seconds applies
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> list[str]:
        return ["max_session_duration"]


check = IAMRoleMaxSessionDuration()

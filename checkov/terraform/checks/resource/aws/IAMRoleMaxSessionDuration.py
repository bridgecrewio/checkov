from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_int
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class IAMRoleMaxSessionDuration(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure IAM role max session duration does not exceed 1 hour"
        id = "CKV_AWS_395"
        supported_resources = ("aws_iam_role",)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        # AWS/Terraform default max_session_duration is 3600 seconds when omitted.
        key = "max_session_duration"
        if key not in conf:
            return CheckResult.PASSED

        duration = conf[key][0]
        if self._is_variable_dependant(duration):
            return CheckResult.UNKNOWN

        duration_int = force_int(duration)
        if duration_int is None:
            return CheckResult.UNKNOWN

        if duration_int <= 3600:
            return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> list[str]:
        return ["max_session_duration"]


check = IAMRoleMaxSessionDuration()

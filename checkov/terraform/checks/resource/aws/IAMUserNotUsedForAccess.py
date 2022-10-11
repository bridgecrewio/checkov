from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class IAMUserNotUsedForAccess(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure access is controlled through SSO and not AWS IAM defined users"
        id = "CKV_AWS_273"
        supported_resources = ('aws_iam_user',)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        return CheckResult.FAILED


check = IAMUserNotUsedForAccess()

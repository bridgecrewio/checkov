from __future__ import annotations

from typing import Any

from checkov.common.util.type_forcers import force_int
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class SecretManagerSecret90days(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Secrets Manager secrets should be rotated within 90 days"
        id = "CKV_AWS_304"
        supported_resources = ("aws_secretsmanager_secret_rotation",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        rules = conf.get("rotation_rules")
        if rules and isinstance(rules, list):
            days = rules[0].get('automatically_after_days')
            if days and isinstance(days, list):
                days = force_int(days[0])
                if days is not None and days < 90:
                    return CheckResult.PASSED
        return CheckResult.FAILED


check = SecretManagerSecret90days()

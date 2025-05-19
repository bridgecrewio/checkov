from __future__ import annotations
import re
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

    def _check_rate_expression(self, expression: str) -> bool:
        rate_match = re.match(r'rate\((\d+)\s+(days?|hours?|minutes?)\)', expression)
        if rate_match:
            value = int(rate_match.group(1))
            unit = rate_match.group(2)

            if unit.startswith('day'):
                return value < 90
            elif unit.startswith('hour'):
                return value < 2160  # 90 days * 24 hours
            elif unit.startswith('minute'):
                return value < 129600  # 90 days * 24 hours * 60 minutes
        return False

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        self.evaluated_keys = ["rotation_rules"]
        rules = conf.get("rotation_rules")
        if rules and isinstance(rules, list):
            rotation_rule = rules[0]

            # Check for automatically_after_days
            days = rotation_rule.get('automatically_after_days')
            if days and isinstance(days, list):
                self.evaluated_keys = ["rotation_rules/[0]/automatically_after_days"]
                days = force_int(days[0])
                if days is not None and days < 90:
                    return CheckResult.PASSED

            # Check for schedule_expression
            schedule = rotation_rule.get('schedule_expression')
            if schedule and isinstance(schedule, list):
                self.evaluated_keys = ["rotation_rules/[0]/schedule_expression"]
                expression = schedule[0]

                if expression.startswith('rate('):
                    return CheckResult.PASSED if self._check_rate_expression(expression) else CheckResult.FAILED
                elif expression.startswith('cron('):
                    # TODO: Handle failing cron expressions
                    return CheckResult.PASSED

        return CheckResult.FAILED


check = SecretManagerSecret90days()

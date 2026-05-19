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
                return value <= 90
            elif unit.startswith('hour'):
                return value <= 2160  # 90 days * 24 hours
            elif unit.startswith('minute'):
                return value <= 129600  # 90 days * 24 hours * 60 minutes
        return False

    def _check_cron_expression(self, expression: str) -> bool:
        """
        Parse AWS EventBridge cron format: cron(minutes hours day-of-month month day-of-week year)
        Returns True (PASS) only if the rotation is guaranteed to run at least every 90 days.
        Fails safe — if parsing fails or is ambiguous, returns False (FAIL).
        """
        inner = expression[5:-1]  # strip cron( and )
        parts = inner.split()
        if len(parts) != 6:
            return False  # malformed cron → fail safe

        month_field = parts[3]

        # Wildcard means runs every month (worst case ~31 days apart) → PASS
        if month_field in ('*', '?'):
            return True

        # Step syntax e.g. */3 means every 3 months → check gap
        if month_field.startswith('*/'):
            try:
                step = int(month_field[2:])
                return (step * 31) <= 90
            except ValueError:
                return False

        # Expand month list/range e.g. "1,4,7,10" or "1-3"
        try:
            months: list[int] = []
            for part in month_field.split(','):
                if '-' in part:
                    start, end = part.split('-', 1)
                    months.extend(range(int(start), int(end) + 1))
                else:
                    months.append(int(part))

            months = sorted(set(months))
            if not months:
                return False

            # Calculate the maximum gap between consecutive months (including wrap-around)
            gaps = [months[i + 1] - months[i] for i in range(len(months) - 1)]
            gaps.append(12 - months[-1] + months[0])  # wrap Jan→Dec gap
            max_gap_months = max(gaps)

            # Worst case: 31 days per month
            return (max_gap_months * 31) <= 90
        except (ValueError, IndexError):
            return False  # parse failure → fail safe

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
                if days is not None and days <= 90:
                    return CheckResult.PASSED

            # Check for schedule_expression
            schedule = rotation_rule.get('schedule_expression')
            if schedule and isinstance(schedule, list):
                self.evaluated_keys = ["rotation_rules/[0]/schedule_expression"]
                expression = schedule[0]

                if expression.startswith('rate('):
                    return CheckResult.PASSED if self._check_rate_expression(expression) else CheckResult.FAILED
                elif expression.startswith('cron('):
                    return CheckResult.PASSED if self._check_cron_expression(expression) else CheckResult.FAILED

        return CheckResult.FAILED


check = SecretManagerSecret90days()

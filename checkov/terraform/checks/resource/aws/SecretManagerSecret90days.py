
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class SecretManagerSecret90days(BaseResourceCheck):

    def __init__(self):
        name = "Ensure Secrets Manager secrets should be rotated within 90 days"
        id = "CKV_AWS_304"
        supported_resources = ["aws_secretsmanager_secret_rotation"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if conf.get("rotation_rules") and isinstance(conf.get("rotation_rules"), list):
            rule = conf.get("rotation_rules")[0]
            if rule.get('automatically_after_days') and isinstance(rule.get('automatically_after_days'), list):
                days = rule.get('automatically_after_days')[0]
                if days < 90:
                    return CheckResult.PASSED
        return CheckResult.FAILED


check = SecretManagerSecret90days()

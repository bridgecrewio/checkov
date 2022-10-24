from typing import Any, Dict, List

from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class DBInstanceLogging(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that respective logs of Amazon Relational Database Service (Amazon RDS) are enabled"
        id = "CKV_AWS_129"
        supported_resources = ["aws_db_instance"]
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "enabled_cloudwatch_logs_exports/[0]"

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        logs_exports = conf.get('enabled_cloudwatch_logs_exports', [[]])
        if not logs_exports:
            return CheckResult.FAILED
        return CheckResult.PASSED if logs_exports[0] else CheckResult.FAILED

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = DBInstanceLogging()

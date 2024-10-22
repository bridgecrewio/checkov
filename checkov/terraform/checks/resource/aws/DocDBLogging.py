from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck

LOG_TYPES = ("profiler", "audit")


class DocDBLogging(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure DocumentDB Logging is enabled"
        id = "CKV_AWS_85"
        supported_resources = ("aws_docdb_cluster",)
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        logs_exports = conf.get("enabled_cloudwatch_logs_exports")
        if logs_exports and isinstance(logs_exports, list):
            if any(elem in logs_exports[0] for elem in LOG_TYPES):
                return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> list[str]:
        return ["enabled_cloudwatch_logs_exports"]


check = DocDBLogging()

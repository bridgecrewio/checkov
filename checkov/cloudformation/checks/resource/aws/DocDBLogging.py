from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck

LOG_TYPES = ("profiler", "audit")


class DocDBLogging(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure DocumentDB Logging is enabled"
        id = "CKV_AWS_85"
        supported_resources = ("AWS::DocDB::DBCluster",)
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        properties = conf.get("Properties")
        if properties:
            logs_exports = properties.get("EnableCloudwatchLogsExports")
            if logs_exports:
                if any(elem in logs_exports for elem in LOG_TYPES):
                    return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> list[str]:
        return ["Properties/EnableCloudwatchLogsExports"]


check = DocDBLogging()

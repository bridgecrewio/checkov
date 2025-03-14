from __future__ import annotations

from typing import Any, List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck

# https://docs.microsoft.com/en-us/azure/templates/microsoft.insights/2016-03-01/logprofiles


class MonitorLogProfileRetentionDays(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure audit profile captures all the activities"
        id = "CKV_AZURE_38"
        supported_resources = ("Microsoft.Insights/logprofiles",)
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        if "properties" in conf and "categories" in conf["properties"]:
            categories = ("Write", "Delete", "Action")
            if all(category in conf["properties"]["categories"] for category in categories):
                return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ["properties", "properties/categories"]


check = MonitorLogProfileRetentionDays()

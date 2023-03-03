from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class RDSRetention(BaseResourceCheck):
    def __init__(self) -> None:
        """
        'sql_collector_status' should be defined and set to "Enabled"  (I know, really, who does that)
         and 'sql_collector_config_value' should be defined and set to 180 or more
        """
        name = "Ensure RDS Instance SQL Collector Retention Period should be greater than 180"
        id = "CKV_ALI_25"
        supported_resources = ("alicloud_db_instance",)
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        collector_status = conf.get("sql_collector_status")
        if collector_status and isinstance(collector_status, list):
            if collector_status[0] != "Enabled":
                self.evaluated_keys = ["sql_collector_status"]
                return CheckResult.FAILED
            collector_config = conf.get("sql_collector_config_value")
            if collector_config and isinstance(collector_config, list):
                self.evaluated_keys = ["sql_collector_config_value"]
                if collector_config[0] >= 180:
                    return CheckResult.PASSED

        return CheckResult.FAILED


check = RDSRetention()

from __future__ import annotations

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_int
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from typing import Any


class DBInstanceBackupRetentionPeriod(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that RDS instances has backup policy"
        id = "CKV_AWS_133"
        supported_resources = ("aws_rds_cluster", "aws_db_instance")
        categories = (CheckCategories.BACKUP_AND_RECOVERY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        key = "backup_retention_period"
        if key in conf.keys():
            period = conf[key][0]
            if self._is_variable_dependant(period):
                return CheckResult.UNKNOWN
            period = force_int(period)
            if period and 0 < period <= 35:
                return CheckResult.PASSED
            return CheckResult.FAILED
        # Default value is 1 which passes ^^^
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> list[str]:
        return ["backup_retention_period"]


check = DBInstanceBackupRetentionPeriod()

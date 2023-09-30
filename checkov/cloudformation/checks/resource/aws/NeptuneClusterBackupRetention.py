from __future__ import annotations

from typing import Any

from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class NeptuneClusterBackupRetention(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that Neptune DB cluster has automated backups enabled with adequate retention"
        id = "CKV_AWS_361"
        supported_resources = ("AWS::Neptune::DBCluster",)
        categories = (CheckCategories.BACKUP_AND_RECOVERY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        backup_retention = conf.get("Properties", {}).get("BackupRetentionPeriod", 1)
        if backup_retention >= 7:
            return CheckResult.PASSED

        return CheckResult.FAILED

    def get_evaluated_keys(self) -> list[str]:
        return ["Properties/BackupRetentionPeriod"]


check = NeptuneClusterBackupRetention()

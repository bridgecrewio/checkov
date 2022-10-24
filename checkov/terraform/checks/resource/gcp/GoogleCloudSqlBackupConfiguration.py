from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class GoogleCloudSqlBackupConfiguration(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure all Cloud SQL database instance have backup configuration enabled"
        id = "CKV_GCP_14"
        supported_resources = ("google_sql_database_instance",)
        categories = (CheckCategories.BACKUP_AND_RECOVERY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if "master_instance_name" in conf:
            return CheckResult.UNKNOWN
        return super().scan_resource_conf(conf)

    def get_inspected_key(self) -> str:
        return "settings/[0]/backup_configuration/[0]/enabled"


check = GoogleCloudSqlBackupConfiguration()

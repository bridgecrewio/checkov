from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class DocDBBackupRetention(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure DocumentDB has an adequate backup retention period"
        id = "CKV_AWS_360"
        supported_resources = ("AWS::DocDB::DBCluster",)
        categories = (CheckCategories.BACKUP_AND_RECOVERY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/BackupRetentionPeriod"

    def scan_resource_conf(self, conf) -> CheckResult:
        properties = conf.get("Properties")
        if properties:
            backup_retention_period = properties.get("BackupRetentionPeriod", 1)
            if backup_retention_period >= 7:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = DocDBBackupRetention()

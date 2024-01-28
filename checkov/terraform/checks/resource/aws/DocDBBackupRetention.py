from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class DocDBBackupRetention(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure DocumentDB has an adequate backup retention period"
        id = "CKV_AWS_360"
        supported_resources = ['aws_docdb_cluster']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "backup_retention_period"

    def scan_resource_conf(self, conf):
        if conf.get("backup_retention_period", [1])[0] >= 7:
            return CheckResult.PASSED
        return CheckResult.FAILED


check = DocDBBackupRetention()

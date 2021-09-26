from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_int
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from typing import List


class DBInstanceBackupRetentionPeriod(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that RDS instances has backup policy"
        id = "CKV_AWS_133"
        supported_resources = ['aws_rds_cluster']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        key = "backup_retention_period"
        if key in conf.keys():
            period = force_int(conf[key][0])
            if period and 0 < period <= 35:
                return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ['backup_retention_period']


check = DBInstanceBackupRetentionPeriod()

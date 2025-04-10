from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class RDSInstanceBackupEnabled(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure RDS instances have backup enabled"
        id = "CKV_AWS_133"
        supported_resources = ("awscc_rds_db_instance",)
        categories = (CheckCategories.BACKUP_AND_RECOVERY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "backup_retention_period"

    def get_forbidden_values(self):
        return [0]


check = RDSInstanceBackupEnabled()

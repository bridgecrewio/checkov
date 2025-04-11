from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class RDSDeletionProtection(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure RDS database has deletion protection enabled"
        id = "CKV_AWS_162"
        supported_resources = ("awscc_rds_db_instance",)
        categories = (CheckCategories.BACKUP_AND_RECOVERY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "deletion_protection"

    def get_expected_value(self):
        return True


check = RDSDeletionProtection()

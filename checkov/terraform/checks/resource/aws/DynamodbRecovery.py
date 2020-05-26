from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class DynamodbRecovery(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Dynamodb point in time recovery (backup) is enabled"
        id = "CKV_AWS_28"
        supported_resources = ['aws_dynamodb_table']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "point_in_time_recovery/[0]/enabled"


check = DynamodbRecovery()

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class DynamodbPointInTimeRecoveryEnabled(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that that point in time recovery is enabled for Amazon DynamoDB tables"
        id = "CKV_AWS_125"
        supported_resources = ['aws_dynamodb_table']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "point_in_time_recovery/[0]/enabled"

    def get_expected_value(self):
        return True


check = DynamodbPointInTimeRecoveryEnabled()

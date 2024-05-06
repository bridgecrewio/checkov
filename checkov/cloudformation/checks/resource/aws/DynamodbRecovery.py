from checkov.common.models.enums import CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class DynamodbRecovery(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure DynamoDB point in time recovery (backup) is enabled"
        id = "CKV_AWS_28"
        supported_resources = ['AWS::DynamoDB::Table']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'Properties/PointInTimeRecoverySpecification/PointInTimeRecoveryEnabled'


check = DynamodbRecovery()

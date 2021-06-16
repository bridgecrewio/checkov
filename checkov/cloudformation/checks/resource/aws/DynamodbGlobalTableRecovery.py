from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


class DynamodbGlobalTableRecovery(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Dynamodb global table point in time recovery (backup) is enabled"
        id = "CKV_AWS_165"
        supported_resources = ['AWS::DynamoDB::GlobalTable']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'Properties/Replicas/[0]/PointInTimeRecoverySpecification/PointInTimeRecoveryEnabled'


check = DynamodbGlobalTableRecovery()

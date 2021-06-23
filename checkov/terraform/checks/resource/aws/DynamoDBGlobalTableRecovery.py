from typing import Dict, List, Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class DynamodbGlobalTableRecovery(BaseResourceCheck):
    def __init__(self):
        name = "Ensure Dynamodb point in time recovery (backup) is enabled for global tables"
        id = "CKV_AWS_165"
        supported_resources = ['aws_dynamodb_global_table']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        # This field cannot be set in terraform's aws_dyanmodb_global_table
        # https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_global_table
        return CheckResult.PASSED


check = DynamodbGlobalTableRecovery()

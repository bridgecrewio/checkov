from typing import Dict, List, Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class DynamoDBTablesEncrypted(BaseResourceCheck):
    def __init__(self):
        name = "Ensure DynamoDB Tables are encrypted using a KMS Customer Managed CMK"
        id = "CKV_AWS_119"
        supported_resources = ["aws_dynamodb_table"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        sse = conf.get("server_side_encryption")
        enabled = sse.get("enabled")
        kms_key_arn = sse.get("kms_key_arn")
        if enabled is True and kms_key_arn != None:
            return CheckResult.PASSED
        else:
            return CheckResult.FAILED


check = DynamoDBTablesEncrypted()

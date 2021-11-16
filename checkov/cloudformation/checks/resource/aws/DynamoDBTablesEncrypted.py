from typing import List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class DynamoDBTablesEncrypted(BaseResourceCheck):
    def __init__(self):
        name = "Ensure DynamoDB Tables are encrypted using a KMS Customer Managed CMK"
        id = "CKV_AWS_119"
        supported_resources = ["AWS::DynamoDB::Table"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        properties = conf.get('Properties')
        if properties is not None:
            sse_config = properties.get('SSESpecification')
            if sse_config is not None:
                sse_enabled = sse_config.get('SSEEnabled')
                sse_key = sse_config.get('KMSMasterKeyId')
                if sse_enabled and sse_key is not None:
                    return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ["Properties/SSESpecification/SSEEnabled", "Properties/SSESpecification/KMSMasterKeyId"]


check = DynamoDBTablesEncrypted()

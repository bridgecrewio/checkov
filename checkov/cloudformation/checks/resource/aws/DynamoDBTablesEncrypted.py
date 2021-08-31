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
        sse_config = conf.get('Properties').get('SSESpecification')
        sse_enabled = sse_config.get('SSEEnabled')
        sse_key = sse_config.get('KMSMasterKeyId')
        if see_enabled is not None and sse_key is not None:
            if sse_enabled is True:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = DynamoDBTablesEncrypted()

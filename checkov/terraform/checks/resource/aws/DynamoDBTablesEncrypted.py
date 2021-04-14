from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class DynamoDBTablesEncrypted(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure DynamoDB Tables are encrypted using KMS"
        id = "CKV_AWS_119"
        supported_resources = ["aws_dynamodb_table"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "server_side_encryption/[0]/enabled"


check = DynamoDBTablesEncrypted()

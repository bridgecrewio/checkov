from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class DynamoDBTablesEncrypted(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure DynamoDB Tables are encrypted using KMS"
        id = "CKV_AWS_119"
        supported_resources = ["aws_dynamodb_table"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "server_side_encryption/[0]/enabled"

    def get_forbidden_values(self):
        return [False, "false"]


check = DynamoDBTablesEncrypted()

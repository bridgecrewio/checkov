from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class DynamodbEncryption(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure Dynamodb is encrypted at rest"
        id = "CKV_AWS_45"
        supported_resources = ['aws_dynamodb_table']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "server_side_encryption/[0]/enabled"

check = DynamodbEncryption()

from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class DynamoDBTableReplicaKMSUsesCMK(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure DynamoDB table replica KMS encryption uses CMK"
        id = "CKV_AWS_271"
        supported_resources = ('aws_dynamodb_table_replica',)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'kms_key_arn'

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = DynamoDBTableReplicaKMSUsesCMK()

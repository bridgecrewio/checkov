from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class KinesisStreamEncryptionType(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Kinesis Stream is securely encrypted"
        id = "CKV_AWS_43"
        supported_resources = ["aws_kinesis_stream"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "encryption_type"

    def get_expected_value(self) -> str:
        return "KMS"


check = KinesisStreamEncryptionType()

from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class KinesisFirehoseDeliveryStreamSSE(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Kinesis Firehose delivery stream is encrypted"
        id = "CKV_AWS_240"
        supported_resources = ["aws_kinesis_firehose_delivery_stream"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.FAILED)

    def get_inspected_key(self) -> str:
        return "server_side_encryption/[0]/enabled"


check = KinesisFirehoseDeliveryStreamSSE()

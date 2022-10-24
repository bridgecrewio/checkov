from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class KinesisFirehoseDeliveryStreamSSE(BaseResourceCheck):
    def __init__(self) -> None:
        """
        Server-side encryption should not be enabled when a kinesis stream is configured
        as the source of the firehose delivery stream.
        """
        name = "Ensure Kinesis Firehose delivery stream is encrypted"
        id = "CKV_AWS_240"
        supported_resources = ["aws_kinesis_firehose_delivery_stream"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if conf.get("kinesis_source_configuration"):
            return CheckResult.UNKNOWN
        if conf.get("server_side_encryption"):
            sse = conf.get("server_side_encryption")[0]
            if sse.get("enabled") == [True]:
                return CheckResult.PASSED
        self.evaluated_keys = ["server_side_encryption/[0]/enabled"]
        return CheckResult.FAILED


check = KinesisFirehoseDeliveryStreamSSE()

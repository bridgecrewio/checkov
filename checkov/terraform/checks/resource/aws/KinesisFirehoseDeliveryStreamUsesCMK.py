from typing import Dict, List, Any

from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class KinesisFirehoseDeliveryStreamUsesCMK(BaseResourceCheck):

    def __init__(self):
        name = "Ensure that Kinesis Firehose Delivery Streams are encrypted with CMK"
        id = "CKV_AWS_241"
        supported_resources = ["aws_kinesis_firehose_delivery_stream"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        if conf.get("kinesis_source_configuration"):
            return CheckResult.UNKNOWN

        if conf.get('server_side_encryption'):
            sse = conf.get('server_side_encryption')[0]
            if sse.get('enabled') != [True]:
                self.evaluated_keys = ['server_side_encryption/[0]/enabled']
                return CheckResult.FAILED
            if sse.get('key_type') != ["CUSTOMER_MANAGED_CMK"]:
                self.evaluated_keys = ['server_side_encryption/[0]/key_type']
                return CheckResult.FAILED
            if not sse.get('key_arn'):
                self.evaluated_keys = ['server_side_encryption/[0]/']
                return CheckResult.FAILED
            if not sse.get('key_arn')[0]:
                self.evaluated_keys = ['server_side_encryption/[0]/key_arn']
                return CheckResult.FAILED
            return CheckResult.PASSED
        return CheckResult.FAILED


check = KinesisFirehoseDeliveryStreamUsesCMK()

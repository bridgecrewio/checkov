from typing import Dict, Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.common.models.consts import ANY_VALUE
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class SQSQueueEncryption(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure all data stored in the SQS queue is encrypted"
        id = "CKV_AWS_27"
        supported_resources = ['aws_sqs_queue']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, Any]) -> CheckResult:
        if conf.get('sqs_managed_sse_enabled'):
            return CheckResult.PASSED
        return super().scan_resource_conf(conf)

    def get_inspected_key(self) -> str:
        return 'kms_master_key_id'

    def get_expected_value(self) -> str:
        return ANY_VALUE


check = SQSQueueEncryption()

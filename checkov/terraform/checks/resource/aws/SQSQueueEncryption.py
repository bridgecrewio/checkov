from typing import Dict, Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class SQSQueueEncryption(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure all data stored in the SQS queue is encrypted"
        id = "CKV_AWS_27"
        supported_resources = ['aws_sqs_queue']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get('sqs_managed_sse_enabled') and isinstance(conf.get('sqs_managed_sse_enabled'), list):
            if conf.get('sqs_managed_sse_enabled')[0]:
                return CheckResult.PASSED
            return CheckResult.FAILED
        if conf.get("kms_master_key_id") and isinstance(conf.get('kms_master_key_id'), list):
            if conf.get('kms_master_key_id')[0]:
                return CheckResult.PASSED
            return CheckResult.FAILED
        return CheckResult.FAILED


check = SQSQueueEncryption()

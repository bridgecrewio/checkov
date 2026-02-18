from __future__ import annotations

from typing import Any, List

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class SQSQueueEncryption(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure all data stored in the SQS queue is encrypted"
        id = "CKV_AWS_27"
        supported_resources = ('awscc_sqs_queue',)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        # Check for SQS managed SSE
        if conf.get("sqs_managed_sse_enabled") and isinstance(conf.get("sqs_managed_sse_enabled"), list):
            if conf.get("sqs_managed_sse_enabled")[0]:
                return CheckResult.PASSED

        # Check for KMS key
        if conf.get("kms_master_key_id") and isinstance(conf.get("kms_master_key_id"), list):
            if conf.get("kms_master_key_id")[0]:
                return CheckResult.PASSED
            
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ["sqs_managed_sse_enabled", "kms_master_key_id"]


check = SQSQueueEncryption()

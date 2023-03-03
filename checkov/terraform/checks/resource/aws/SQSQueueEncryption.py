from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class SQSQueueEncryption(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure all data stored in the SQS queue is encrypted"
        id = "CKV_AWS_27"
        supported_resources = ('aws_sqs_queue',)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        sqs_managed_sse_enabled = conf.get("sqs_managed_sse_enabled")
        if sqs_managed_sse_enabled and isinstance(sqs_managed_sse_enabled, list):
            if sqs_managed_sse_enabled[0]:
                return CheckResult.PASSED
            return CheckResult.FAILED

        kms_master_key_id = conf.get("kms_master_key_id")
        if kms_master_key_id and isinstance(kms_master_key_id, list):
            if kms_master_key_id[0]:
                return CheckResult.PASSED
            return CheckResult.FAILED
        return CheckResult.FAILED


check = SQSQueueEncryption()

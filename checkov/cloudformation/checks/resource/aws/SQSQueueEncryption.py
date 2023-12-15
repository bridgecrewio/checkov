from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class SQSQueueEncryption(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure all data stored in the SQS queue is encrypted"
        id = "CKV_AWS_27"
        supported_resources = ['AWS::SQS::Queue']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    # def get_inspected_key(self) -> str:
    #     return 'Properties/KmsMasterKeyId'

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if conf.get("Properties") and isinstance(conf.get("Properties"), dict):
            properties = conf.get("Properties")
            sqs_managed_sse_enabled = properties.get("SqsManagedSseEnabled")
            if sqs_managed_sse_enabled and isinstance(sqs_managed_sse_enabled, bool):
                return CheckResult.PASSED

            kms_master_key_id = properties.get("KmsMasterKeyId")
            if kms_master_key_id and isinstance(kms_master_key_id, str):
                return CheckResult.PASSED

        return CheckResult.FAILED


check = SQSQueueEncryption()

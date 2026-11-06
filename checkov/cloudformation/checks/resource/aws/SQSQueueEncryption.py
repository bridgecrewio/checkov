from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class SQSQueueEncryption(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure all data stored in the SQS queue is encrypted"
        id = "CKV_AWS_27"
        supported_resources = ['AWS::SQS::Queue']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'Properties/KmsMasterKeyId'

    def get_expected_value(self) -> Any:
        return ANY_VALUE

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        # SQS-managed SSE is a valid alternative to a customer KMS key, so a queue
        # that enables it should pass even when KmsMasterKeyId is absent.
        properties = conf.get("Properties")
        if isinstance(properties, dict):
            sqs_managed_sse = properties.get("SqsManagedSseEnabled")
            # The parser yields a real bool for `true`/`false`, but a quoted value
            # like "false" comes through as a (truthy) string, so check both forms.
            if sqs_managed_sse is True or (isinstance(sqs_managed_sse, str) and sqs_managed_sse.lower() == "true"):
                return CheckResult.PASSED

        return super().scan_resource_conf(conf)


check = SQSQueueEncryption()

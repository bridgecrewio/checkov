from typing import Any

from checkov.common.models.enums import CheckCategories
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


check = SQSQueueEncryption()

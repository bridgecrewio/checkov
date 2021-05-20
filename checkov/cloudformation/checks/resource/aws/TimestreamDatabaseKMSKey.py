from typing import Any

from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories


class TimestreamDatabaseKMSKey(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Timestream database is encrypted with KMS CMK"
        id = "CKV_AWS_160"
        supported_resources = ["AWS::Timestream::Database"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "Properties/KmsKeyId"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = TimestreamDatabaseKMSKey()

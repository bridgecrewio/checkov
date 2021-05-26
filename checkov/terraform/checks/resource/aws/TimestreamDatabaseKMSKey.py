from typing import Any

from checkov.common.models.consts import ANY_VALUE
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class TimestreamDatabaseKMSKey(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Timestream database is encrypted with KMS CMK"
        id = "CKV_AWS_160"
        supported_resources = ["aws_timestreamwrite_database"]
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "kms_key_id"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = TimestreamDatabaseKMSKey()

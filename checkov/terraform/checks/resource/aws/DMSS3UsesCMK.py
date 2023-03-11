from __future__ import annotations

from typing import Any

from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE


class DMSS3UsesCMK(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure DMS S3 uses Customer Managed Key (CMK)"
        id = "CKV_AWS_298"
        supported_resources = ("aws_dms_s3_endpoint",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "kms_key_arn"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = DMSS3UsesCMK()

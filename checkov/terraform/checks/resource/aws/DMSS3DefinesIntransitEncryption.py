from __future__ import annotations

from typing import Any

from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class DMSS3DefinesIntransitEncryption(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure DMS S3 defines in-transit encryption"
        id = "CKV_AWS_299"
        supported_resources = ("aws_dms_s3_endpoint",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'ssl_mode'

    def get_expected_values(self) -> list[Any]:
        return ["require", "verify-ca", "verify-full"]


check = DMSS3DefinesIntransitEncryption()

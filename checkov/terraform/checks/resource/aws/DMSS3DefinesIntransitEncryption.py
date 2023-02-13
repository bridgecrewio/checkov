from __future__ import annotations

from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE


class DMSS3DefinesIntransitEncryption(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure DMS S3 Defines In-transit Encryption"
        id = "CKV_AWS_294"
        supported_resources = ("aws_dms_s3_endpoint",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'ssl_mode'

    def get_expected_values(self):
        return ["require", "verify-ca", "verify-full"]


check = DMSS3DefinesIntransitEncryption()

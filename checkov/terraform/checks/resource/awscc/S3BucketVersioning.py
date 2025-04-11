from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class S3BucketVersioning(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure all data stored in the S3 bucket have versioning enabled"
        id = "CKV_AWS_21"
        supported_resources = ("awscc_s3_bucket",)
        categories = (CheckCategories.BACKUP_AND_RECOVERY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "versioning_configuration/[0]/status"

    def get_expected_value(self) -> Any:
        return "Enabled"


check = S3BucketVersioning()

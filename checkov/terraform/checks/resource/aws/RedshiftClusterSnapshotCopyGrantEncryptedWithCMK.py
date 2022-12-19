from typing import Any

from checkov.common.models.consts import ANY_VALUE
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class RedshiftSnapshotCopyGrantEncryptedWithCMK(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure RedShift snapshot copy is encrypted by KMS using a customer managed Key (CMK)"
        id = "CKV_AWS_281"
        supported_resources = ("aws_redshift_snapshot_copy_grant",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "kms_key_id"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = RedshiftSnapshotCopyGrantEncryptedWithCMK()

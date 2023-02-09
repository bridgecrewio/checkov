from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class DiskEncryptedWithCMK(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Disk is encrypted with Customer Master Key"
        id = "CKV_ALI_8"
        supported_resources = ("alicloud_disk",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if conf.get("snapshot_id"):
            return CheckResult.UNKNOWN
        encrypted = conf.get("encrypted")
        if encrypted and encrypted == [True]:
            if conf.get("kms_key_id"):
                return CheckResult.PASSED
        return CheckResult.FAILED


check = DiskEncryptedWithCMK()

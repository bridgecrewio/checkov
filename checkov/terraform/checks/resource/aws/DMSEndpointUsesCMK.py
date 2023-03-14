from __future__ import annotations

from typing import Any

from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class DMSEndpointUsesCMK(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure DMS endpoint uses Customer Managed Key (CMK)"
        id = "CKV_AWS_296"
        supported_resources = ("aws_dms_endpoint",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        engine_name = conf.get("engine_name")
        if engine_name and isinstance(engine_name, list) and engine_name[0] == "s3":
            self.evaluated_keys = ["s3_settings"]
            s3_settings = conf.get("s3_settings")
            if s3_settings and isinstance(s3_settings, list):
                self.evaluated_keys = ["s3_settings/server_side_encryption_kms_key_id"]
                settings = s3_settings[0]
                if settings.get("server_side_encryption_kms_key_id"):
                    return CheckResult.PASSED
            return CheckResult.FAILED

        self.evaluated_keys = ["kms_key_arn"]
        kms_key = conf.get("kms_key_arn")
        if kms_key and isinstance(kms_key, list) and kms_key[0]:
            return CheckResult.PASSED

        return CheckResult.FAILED


check = DMSEndpointUsesCMK()

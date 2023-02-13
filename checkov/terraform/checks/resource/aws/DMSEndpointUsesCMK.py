from __future__ import annotations

from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories,CheckResult


class DMSEndpointUsesCMK(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure DMS endpoint Uses Customer managed key"
        id = "CKV_AWS_292"
        supported_resources = ("aws_dms_endpoint",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'engine_name' in conf and isinstance(conf.get('engine_name'), list):
            engine = conf.get("engine_name")[0]
            if engine == "s3":
                self.evaluated_keys = ['s3_settings']
                if conf.get("s3_settings") and isinstance(conf.get("s3_settings"), list):
                    settings = conf.get("s3_settings")[0]
                    if settings.get('server_side_encryption_kms_key_id'):
                        return CheckResult.PASSED
                    self.evaluated_keys = ['s3_settings/server_side_encryption_kms_key_id']
                return CheckResult.FAILED
            else:
                if 'kms_key_arn' in conf and isinstance(conf.get('kms_key_arn'), list):
                    if conf.get('kms_key_arn')[0]:
                        return CheckResult.PASSED
                self.evaluated_keys = ['kms_key_arn']
            return CheckResult.FAILED

        return CheckResult.FAILED


check = DMSEndpointUsesCMK()

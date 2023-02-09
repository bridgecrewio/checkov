from __future__ import annotations

from typing import Any

from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class LambdaEnvironmentEncryptionSettings(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Check encryption settings for Lambda environmental variable"
        id = "CKV_AWS_173"
        supported_resources = ("aws_lambda_function",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        # check that if I have env vars I have a KMS key
        if len(conf.get("environment", [])):
            if "kms_key_arn" in conf:
                if conf["kms_key_arn"] == [""]:
                    self.evaluated_keys = ["environment/kms_key_arn"]
                    return CheckResult.FAILED
                return CheckResult.PASSED
            self.evaluated_keys = ["environment"]
            return CheckResult.FAILED

        # no env vars so should be no key as that causes state mismatch
        if "kms_key_arn" in conf:
            if not len(conf["kms_key_arn"]):
                return CheckResult.PASSED
            return CheckResult.FAILED
        # neither env vars nor kms key
        return CheckResult.UNKNOWN

    def get_evaluated_keys(self) -> list[str]:
        return ["environment/[0]/variables"]


check = LambdaEnvironmentEncryptionSettings()

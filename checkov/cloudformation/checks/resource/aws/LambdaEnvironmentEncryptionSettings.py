from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class LambdaEnvironmentEncryptionSettings(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Check encryption settings for Lambda environment variable"
        id = "CKV_AWS_173"
        supported_resources = ("AWS::Lambda::Function", "AWS::Serverless::Function")
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        properties = conf.get("Properties")
        if properties is not None:
            env = properties.get("Environment")
            if env is not None:
                if not isinstance(env, dict):
                    return CheckResult.UNKNOWN
                elif env.get("Variables") and not properties.get("KmsKeyArn"):
                    return CheckResult.FAILED
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> list[str]:
        return ["Properties/KmsKeyArn"]


check = LambdaEnvironmentEncryptionSettings()

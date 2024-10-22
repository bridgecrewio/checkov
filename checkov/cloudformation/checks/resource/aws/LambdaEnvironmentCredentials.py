from __future__ import annotations

from typing import Any

from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.secrets import AWS, GENERAL, get_secrets_from_string


class LambdaEnvironmentCredentials(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure no hard-coded secrets exist in Lambda environment"
        id = "CKV_AWS_45"
        supported_resources = ("AWS::Lambda::Function", "AWS::Serverless::Function")
        categories = (CheckCategories.SECRETS,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        self.evaluated_keys = ["Properties/Environment/Variables"]
        properties = conf.get("Properties")
        if isinstance(properties, dict):
            environment = properties.get("Environment")
            if environment and isinstance(environment, dict):
                variables = environment.get("Variables")
                if variables and isinstance(variables, dict):
                    for var_name, value in variables.items():
                        if isinstance(value, dict):
                            # if it is a resolved instrinsic function like !Ref: xyz, then it can't be a secret
                            continue

                        secrets = get_secrets_from_string(str(value), AWS, GENERAL)
                        if secrets:
                            self.evaluated_keys = [f"Properties/Environment/Variables/{var_name}"]
                            for idx, secret in enumerate(secrets):
                                conf[f'{self.id}_secret_{idx}'] = secret
                            return CheckResult.FAILED

        return CheckResult.PASSED


check = LambdaEnvironmentCredentials()

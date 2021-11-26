from typing import Dict, List, Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.util.secrets import string_has_secrets, AWS, GENERAL
from checkov.common.util.type_forcers import force_list


class LambdaEnvironmentCredentials(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure no hard-coded secrets exist in lambda environment"
        id = "CKV_AWS_45"
        supported_resources = ["aws_lambda_function"]
        categories = [CheckCategories.SECRETS]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        environment = conf.get("environment", [])
        if environment and isinstance(environment[0], dict):
            self.evaluated_keys = ["environment"]

            variables = force_list(environment[0].get("variables", []))
            if variables and isinstance(variables[0], dict):
                self.evaluated_keys = ["environment/[0]/variables"]

                violated_envs = set()
                for key, values in variables[0].items():
                    # variables can be a string, which in this case it points to a variable
                    for value in [v for v in force_list(values) if isinstance(v, str)]:
                        if string_has_secrets(value, AWS, GENERAL):
                            violated_envs.add(key)

                if violated_envs:
                    self.evaluated_keys = [f"environment/[0]/variables/[0]/{env_key}" for env_key in violated_envs]

                    return CheckResult.FAILED
        return CheckResult.PASSED


check = LambdaEnvironmentCredentials()

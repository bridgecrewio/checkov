from __future__ import annotations

import re
from typing import Any

from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.secrets import AWS, GENERAL, PASSWORD, get_secrets_from_string


class ParameterStoreCredentials(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure no hard-coded secrets exist in Parameter Store values"
        id = "CKV_AWS_384"
        supported_resources = ("AWS::SSM::Parameter",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def is_dynamic_value(self, value: str) -> bool:
        patterns = [
            r"\$\{.*?\}",  # ${...}
            r"\{\{.*?\}\}",  # {{...}}
            r"\$\(.*?\)",  # $(...)
            r"!Ref\s+\w+",  # !Ref SomeResource
            r"!Sub\s+'.*?'",  # !Sub '...'
        ]
        return any(re.search(pattern, value) for pattern in patterns)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        self.evaluated_keys = ["Properties/Value"]
        properties = conf.get("Properties")
        if isinstance(properties, dict):
            name = properties.get("Name")
            if name and re.match("(?i).*secret.*|.*api_?key.*", str(name)):
                value = properties.get("Value")
                if value:
                    # If unresolved variable, then pass
                    if isinstance(value, dict):
                        return CheckResult.PASSED
                    # If unresolved variable, then pass 2
                    if re.match(r".*\$\{.*}.*", value):
                        return CheckResult.PASSED
                    if (re.match("(?i)(.*test.*|.*example.*)", name) or
                            re.match("(?i)(.*test.*|.*example.*)", value)):
                        return CheckResult.PASSED
                    secret = get_secrets_from_string(str(value), AWS, GENERAL, PASSWORD)
                    if secret:
                        return CheckResult.FAILED
        return CheckResult.PASSED


check = ParameterStoreCredentials()

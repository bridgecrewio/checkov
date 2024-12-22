from __future__ import annotations

import re
from typing import Any

from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class ParameterStoreCredentials(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure no hard-coded secrets exist in Parameter Store values"
        id = "CKV_AWS_899"
        supported_resources = ("AWS::SSM::Parameter",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        self.evaluated_keys = ["Properties/Value"]
        properties = conf.get("Properties")
        if isinstance(properties, dict):
            name = properties.get("Name")
            if name and re.match("(?i).*secret.*|.*api_?key.*", name):
                value = properties.get("Value")
                if value:
                    # If unresolved variable, then pass
                    if isinstance(value, dict):
                        return CheckResult.PASSED
                    # If unresolved variable, then pass 2
                    if re.match(".*\$\{.*}.*", value):
                        return CheckResult.PASSED
                    if (re.match("(?i)(.*test.*|.*example.*)",name) or
                            re.match("(?i)(.*test.*|.*example.*)", value)):
                        return CheckResult.PASSED
                    return CheckResult.FAILED
        return CheckResult.PASSED


check = ParameterStoreCredentials()

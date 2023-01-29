from __future__ import annotations

from typing import Any

from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class PolicyNoApplicationAny(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure security rules do not have 'applications' set to 'any' "
        id = "CKV_PAN_5"
        supported_resources = ('panos_security_policy', 'panos_security_rule_group')
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        # Check there is a rule defined in the resource
        if 'rule' in conf:

            # Report the area of evaluation
            self.evaluated_keys = ['rule']

            # Get all the rules defined in the resource
            rules = conf['rule']

            # Iterate over each rule
            for secrule in rules:

                # Check if applications is defined in the resource
                if 'applications' in secrule:

                    # If applications is defined, get the value
                    apps = secrule['applications']

                    # The value "any" is overly permissive and is therefore a fail. The value "any" can only appear on its on, "any" with any other values in the list is rejected by Terraform during apply stage
                    if apps[0][0] == "any":
                        return CheckResult.FAILED
                    # Any non-any value is specifying an application, which is a pass
                else:
                    # If "applications" attribute is not defined, this is not valid and will fail during Terraform plan stage, and should therefore be a fail
                    return CheckResult.FAILED

            # No "any" found for the "applications" attribute for any rules, therefore we have a pass
            return CheckResult.PASSED

        # If there's no rules we have nothing to check
        return CheckResult.UNKNOWN


check = PolicyNoApplicationAny()

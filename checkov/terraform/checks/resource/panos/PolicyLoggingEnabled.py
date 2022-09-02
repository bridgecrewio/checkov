from __future__ import annotations

from typing import Any

from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class PolicyLoggingEnabled(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure logging at session end is enabled within security policies"
        id = "CKV_PAN_10"
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

                # Check if logging at session end is defined in the resource
                if 'log_end' in secrule:

                    # If logging at session end is defined, get the value
                    logstatus = secrule['log_end']

                    # Setting log_end to false is a fail, logging will be disabled
                    if not logstatus[0]:
                        return CheckResult.FAILED
                    # The other value for log_end is true, which is a pass

            # If no fails were found in the rules, this is a pass
            # Also, if no log_end attributes were explicitly set, the default is true, which is also a pass
            return CheckResult.PASSED

        # If there's no rules we have nothing to check
        return CheckResult.UNKNOWN


check = PolicyLoggingEnabled()

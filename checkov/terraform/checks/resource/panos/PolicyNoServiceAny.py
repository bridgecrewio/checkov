from __future__ import annotations

from typing import Any

from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class PolicyNoServiceAny(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure security rules do not have 'services' set to 'any' "
        id = "CKV_PAN_6"
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

                # Check if services is defined in the resource
                if 'services' in secrule:

                    # If services is defined, get the value
                    services = secrule['services']

                    # The value "any" is overly permissive and is therefore a fail. The value "any" can only appear on its on, "any" with any other values in the list is rejected by Terraform during apply stage
                    if services[0][0] == "any":
                        return CheckResult.FAILED
                    # Any non-any value is specifying an service, which is a pass
                else:
                    # If "services" attribute is not defined, this is not valid and will fail during Terraform plan stage, and should therefore be a fail
                    return CheckResult.FAILED

            # No "any" found for the "services" attribute for any rules, therefore we have a pass
            return CheckResult.PASSED

        # If there's no rules we have nothing to check
        return CheckResult.UNKNOWN


check = PolicyNoServiceAny()

from __future__ import annotations

from typing import Any

from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class PolicyNoDSRI(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure DSRI is not enabled within security policies"
        id = "CKV_PAN_4"
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

                # Check if DSRI is defined in the resource
                if 'disable_server_response_inspection' in secrule:

                    # If DSRI is defined, get the value
                    dsriflag = secrule['disable_server_response_inspection']

                    # Setting DSRI to true is a fail as server-to-client inspection will be disabled
                    if dsriflag[0]:
                        return CheckResult.FAILED

            # The other value for DSRI is false, which is a pass
            # Also, if the DSRI attribute is not explicitly set, the default is false, which is also a pass
            return CheckResult.PASSED

        # If there's no rules we have nothing to check
        return CheckResult.UNKNOWN


check = PolicyNoDSRI()

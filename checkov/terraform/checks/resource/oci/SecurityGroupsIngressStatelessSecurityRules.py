from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class SecurityGroupsIngressStatelessSecurityRules(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure security group has stateless ingress security rules"
        id = "CKV_OCI_21"
        supported_resources = ('oci_core_network_security_group_security_rule',)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        stateless = conf.get('stateless')
        direction = conf.get('direction')
        self.evaluated_keys = ["direction"]
        if direction and direction[0] == 'INGRESS':
            self.evaluated_keys.append("stateless")
            if stateless is None or stateless[0] is False:
                return CheckResult.FAILED
            return CheckResult.PASSED
        return CheckResult.UNKNOWN


check = SecurityGroupsIngressStatelessSecurityRules()

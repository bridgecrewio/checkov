from typing import Dict, List, Any

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class FirewallInboundPolicy(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Inbound Firewall Policy is not set to ACCEPT"
        id = "CKV_LIN_5"
        supported_resources = ["linode_firewall"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        if conf.get("inbound_policy") == ["DROP"]:
            return CheckResult.PASSED
        return CheckResult.FAILED


check = FirewallInboundPolicy()

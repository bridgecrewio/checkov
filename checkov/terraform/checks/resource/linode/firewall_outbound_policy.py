from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class FirewallOutboundPolicy(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Outbound Firewall Policy is not set to ACCEPT"
        id = "CKV_LIN_6"
        supported_resources = ["linode_firewall"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "outbound_policy"

    def get_expected_value(self) -> Any:
        return "DROP"


check = FirewallOutboundPolicy()

from typing import Any

from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from checkov.common.models.consts import ANY_VALUE


class NetworkFirewallPolicyDefinesCMK(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure Network Firewall Policy defines an encryption configuration that uses a " \
               "customer managed Key (CMK)"
        id = "CKV_AWS_346"
        supported_resources = ("aws_networkfirewall_firewall_policy",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "encryption_configuration/[0]/key_id"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = NetworkFirewallPolicyDefinesCMK()

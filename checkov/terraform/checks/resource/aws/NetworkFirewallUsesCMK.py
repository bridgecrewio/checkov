from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories
from typing import Any
from checkov.common.models.consts import ANY_VALUE


class NetworkFirewallUsesCMK(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure that Network firewall encryption is via a CMK"
        id = "CKV_AWS_345"
        supported_resources = ['aws_networkfirewall_firewall', 'aws_networkfirewall_rule_group']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'encryption_configuration/[0]/key_id'

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = NetworkFirewallUsesCMK()

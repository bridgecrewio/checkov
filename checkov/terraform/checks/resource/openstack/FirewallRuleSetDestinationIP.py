from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.consts import ANY_VALUE


class FirewallRuleSetDestinationIP(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure firewall rule set a destination IP"
        id = "CKV_OPENSTACK_5"
        supported_resources = ['openstack_fw_rule_v1']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'destination_ip_address'

    def get_expected_value(self) -> str:
        return ANY_VALUE


check = FirewallRuleSetDestinationIP()

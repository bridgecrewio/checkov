from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.consts import ANY_VALUE


class FirewallRuleSetDestinationIP(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure firewall rule set a destination IP"
        id = "CKV_OPENSTACK_5"
        supported_resources = ['openstack_fw_rule_v1']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_attribute_result=CheckResult.FAILED)

    def get_inspected_key(self) -> str:
        return 'destination_ip_address'

    def get_forbidden_values(self) -> str:
        return ["0.0.0.0/0", "0.0.0.0"] # nosec

check = FirewallRuleSetDestinationIP()

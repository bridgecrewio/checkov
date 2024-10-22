from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class NetworkFirewallDeletionProtection(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure that Network firewalls have deletion protection enabled"
        id = "CKV_AWS_344"
        supported_resources = ['aws_networkfirewall_firewall']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources,
                         missing_block_result=CheckResult.FAILED)

    def get_inspected_key(self):
        return 'delete_protection'


check = NetworkFirewallDeletionProtection()

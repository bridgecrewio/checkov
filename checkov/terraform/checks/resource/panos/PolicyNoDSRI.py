from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class PolicyNoDSRI(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure DSRI is not enabled within security policies"
        id = "CKV_PAN_4"
        supported_resources = ['panos_security_policy','panos_security_rule_group']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'rule/[0]/disable_server_response_inspection'

    def get_forbidden_values(self):
        return [True]


check = PolicyNoDSRI()

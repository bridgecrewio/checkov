from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class InterfaceMgmtProfileNoTelnet(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure plain-text management Telnet is not enabled for an Interface Management Profile"
        id = "CKV_PAN_3"
        supported_resources = ['panos_management_profile']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'telnet'

    def get_forbidden_values(self):
        return [True]


check = InterfaceMgmtProfileNoTelnet()

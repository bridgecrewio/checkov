from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class ServerPublicIP(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure Server instance should not have public IP."
        id = "CKV_NCP_23"
        supported_resource = ('ncloud_public_ip',)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resource)

    def get_inspected_key(self):
        return 'server_instance_no'

    def get_forbidden_values(self):
        return [ANY_VALUE]


check = ServerPublicIP()

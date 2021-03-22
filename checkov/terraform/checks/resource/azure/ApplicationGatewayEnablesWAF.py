from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck


class ApplicationGatewayEnablesWAF(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure that Application Gateway enables WAF"
        id = "CKV_AZURE_120"
        supported_resources = ['azurerm_application_gateway']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "waf_configuration/[0]/enabled"


check = ApplicationGatewayEnablesWAF()

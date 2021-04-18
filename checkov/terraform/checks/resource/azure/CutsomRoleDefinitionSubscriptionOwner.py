from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck


class CustomRoleDefinitionSubscriptionOwner(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that no custom subscription owner roles are created"
        id = "CKV_AZURE_39"
        supported_resources = ['azurerm_role_definition']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if 'actions' in conf['permissions'][0] and '*' in conf['permissions'][0]['actions'][0]:
            return CheckResult.FAILED
        return CheckResult.PASSED


check = CustomRoleDefinitionSubscriptionOwner()

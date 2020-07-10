from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck
import re


class CustomRoleDefinitionSubscriptionOwner(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that no custom subscription owner roles are created"
        id = "CKV_AZURE_39"
        supported_resources = ['azurerm_role_definition']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        subscription = re.compile(r"\/|\/subscriptions\/[\w\d-]+$|\${(data|resource)\.azurerm_subscription\.")
        if any(re.match(subscription, scope) for scope in conf['assignable_scopes'][0]):
            if 'actions' in conf['permissions'][0] and '*' in conf['permissions'][0]['actions'][0]:
                return CheckResult.FAILED
        return CheckResult.PASSED


check = CustomRoleDefinitionSubscriptionOwner()

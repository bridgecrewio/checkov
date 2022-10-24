from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceCheck
from typing import List


class CustomRoleDefinitionSubscriptionOwner(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that no custom subscription owner roles are created"
        id = "CKV_AZURE_39"
        supported_resources = ['azurerm_role_definition']
        categories = [CheckCategories.IAM]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        actions = conf.get("permissions", [{}])[0].get("actions", [""])
        if actions and "*" in actions[0]:
            return CheckResult.FAILED
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ['permissions/[0]/actions']


check = CustomRoleDefinitionSubscriptionOwner()

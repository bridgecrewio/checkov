from __future__ import annotations

from typing import Any, List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck
import re

SUBSCRIPTION = re.compile(r"\/|\/subscriptions\/[\w\d-]+$|\[subscription\(\).id\]")

# https://docs.microsoft.com/en-us/azure/role-based-access-control/custom-roles-template
# https://docs.microsoft.com/en-us/azure/role-based-access-control/role-definitions
# https://docs.microsoft.com/en-us/azure/templates/microsoft.authorization/2018-01-01-preview/roledefinitions


class CustomRoleDefinitionSubscriptionOwner(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure that no custom subscription owner roles are created"
        id = "CKV_AZURE_39"
        supported_resources = ("Microsoft.Authorization/roleDefinitions",)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        if "properties" in conf:
            if "assignableScopes" in conf["properties"]:
                if any(
                    isinstance(scope, str) and re.match(SUBSCRIPTION, scope)
                    for scope in conf["properties"]["assignableScopes"]
                ):
                    if "permissions" in conf["properties"]:
                        if conf["properties"]["permissions"]:
                            for permission in conf["properties"]["permissions"]:
                                if "actions" in permission and "*" in permission["actions"]:
                                    return CheckResult.FAILED
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ["properties/assignableScopes", "properties/permissions/actions"]


check = CustomRoleDefinitionSubscriptionOwner()

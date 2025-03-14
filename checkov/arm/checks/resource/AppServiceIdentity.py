from __future__ import annotations

from typing import Any, List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck


class AppServiceIdentity(BaseResourceCheck):
    def __init__(self) -> None:
        # https://docs.microsoft.com/en-us/azure/templates/microsoft.web/2019-08-01/sites#ManagedServiceIdentity
        # https://docs.microsoft.com/en-us/azure/app-service/overview-managed-identity
        # https://docs.microsoft.com/en-us/azure/app-service/samples-resource-manager-templates
        name = "Ensure that Register with Azure Active Directory is enabled on App Service"
        id = "CKV_AZURE_16"
        supported_resources = ('Microsoft.Web/sites',)
        categories = (CheckCategories.IAM,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        if "identity" in conf:
            if "type" in conf["identity"]:
                if conf["identity"]["type"] == "SystemAssigned":
                    return CheckResult.PASSED
                elif conf["identity"]["type"] == "UserAssigned":
                    if "userAssignedIdentities" in conf["identity"]:
                        if conf["identity"]["userAssignedIdentities"]:
                            return CheckResult.PASSED
        return CheckResult.FAILED

    def get_evaluated_keys(self) -> List[str]:
        return ['identity', 'identity/type', 'identity/userAssignedIdentities']


check = AppServiceIdentity()

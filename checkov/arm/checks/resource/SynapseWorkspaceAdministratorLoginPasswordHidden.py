from __future__ import annotations

from typing import Any, List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck


class SynapseWorkspaceAdministratorLoginPasswordHidden(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Azure Synapse Workspace administrator login password is not exposed"
        id = "CKV_AZURE_239"
        supported_resources = ['Microsoft.Synapse/workspaces']
        categories = [CheckCategories.SECRETS]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        if conf.get("properties", {}).get("sqlAdministratorLoginPassword"):
            return CheckResult.FAILED
        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ['properties/sqlAdministratorLoginPassword']


check = SynapseWorkspaceAdministratorLoginPasswordHidden()

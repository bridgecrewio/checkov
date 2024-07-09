from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck


class SynapseLogMonitoringEnabledForSQLPool(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure log monitoring is enabled for Synapse SQL Pool"
        id = "CKV2_AZURE_54"
        supported_resources = ('Microsoft.Synapse/workspaces',)
        categories = (CheckCategories.LOGGING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)


    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        if "resources" in conf:
            if conf["resources"]:
                for resource in conf["resources"]:
                    if "type" in resource:
                        if resource["type"] == "Microsoft.Synapse/workspaces":
                            if "parameters" in resource:
                                if ("sqlAdministratorLoginPassword" in resource["parameters"]):
                                    return CheckResult.FAILED
        return CheckResult.PASSED


check = SynapseWorkspaceAdministratorLoginPasswordHidden()

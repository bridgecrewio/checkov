from __future__ import annotations
from typing import Any
from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class SynapseWorkspaceCMKEncryption(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Azure Synapse Workspace is encrypted with a CMK"
        id = "CKV_AZURE_240"
        supported_resources = ['Microsoft.Synapse/workspaces']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        encryption = conf.get("properties", {}).get("encryption", {})

        if "cmk" in encryption:
            return CheckResult.PASSED

        return CheckResult.FAILED

    def get_evaluated_keys(self) -> list[str]:
        return ['properties', 'properties/encryption']


check = SynapseWorkspaceCMKEncryption()

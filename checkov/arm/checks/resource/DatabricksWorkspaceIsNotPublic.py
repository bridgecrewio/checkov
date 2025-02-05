from __future__ import annotations

from typing import Any, List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.arm.base_resource_check import BaseResourceCheck
from checkov.common.util.data_structures_utils import find_in_dict


class DatabricksWorkspaceIsNotPublic(BaseResourceCheck):
    def __init__(self) -> None:
        # https://learn.microsoft.com/en-us/azure/templates/microsoft.databricks/workspaces?pivots=deployment-language-arm-template
        name = "Ensure Databricks Workspace data plane to control plane communication happens over private link"
        id = "CKV_AZURE_158"
        supported_resources = ("Microsoft.Databricks/workspaces",)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, Any]) -> CheckResult:
        public_network_access = find_in_dict(input_dict=conf, key_path="properties/publicNetworkAccess")
        if not public_network_access or public_network_access == "Enabled":
            return CheckResult.FAILED

        return CheckResult.PASSED

    def get_evaluated_keys(self) -> List[str]:
        return ["properties", "properties/publicNetworkAccess"]


check = DatabricksWorkspaceIsNotPublic()

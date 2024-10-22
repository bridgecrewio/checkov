from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckCategories
from checkov.arm.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class SynapseWorkspaceEnablesManagedVirtualNetworks(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure Synapse workspaces enables managed virtual networks"
        id = "CKV_AZURE_58"
        supported_resources = ['Microsoft.Synapse/workspaces']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'properties/managedVirtualNetwork'

    def get_forbidden_values(self) -> list[Any]:
        return ["default"]


check = SynapseWorkspaceEnablesManagedVirtualNetworks()

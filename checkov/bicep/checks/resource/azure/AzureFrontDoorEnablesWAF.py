from __future__ import annotations
from checkov.common.models.consts import ANY_VALUE
from typing import Any

from checkov.bicep.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories


class AzureFrontDoorEnablesWAF(BaseResourceValueCheck):
    def __init__(self) -> None:
        name = "Ensure that Azure Front Door enables WAF"
        id = "CKV_AZURE_121"
        supported_resources = ['Microsoft.Network/frontDoors']
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "properties/frontendEndpoints/[0]/properties/webApplicationFirewallPolicyLink/id"

    def get_expected_value(self) -> Any:
        return ANY_VALUE


check = AzureFrontDoorEnablesWAF()

from __future__ import annotations

from typing import Any

from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckCategories


class MSKClusterNodesArePrivate(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure MSK nodes are private"
        id = "CKV_AWS_291"
        supported_resources = ('aws_msk_cluster',)
        categories = (CheckCategories.NETWORKING,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "broker_node_group_info/[0]/connectivity_info/[0]/public_access/[0]/type"

    def get_forbidden_values(self) -> list[Any]:
        return ["SERVICE_PROVIDED_EIPS"]


check = MSKClusterNodesArePrivate()

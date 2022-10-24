from __future__ import annotations

from typing import Any

from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckCategories


class GKEEnableShieldedNodes(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure Shielded GKE Nodes are Enabled"
        id = "CKV_GCP_71"
        supported_resources = ('google_container_cluster',)
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return 'enable_shielded_nodes'

    def get_forbidden_values(self) -> list[Any]:
        return [False]


check = GKEEnableShieldedNodes()

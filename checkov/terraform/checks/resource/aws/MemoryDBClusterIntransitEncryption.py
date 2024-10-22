from __future__ import annotations

from typing import Any

from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck
from checkov.common.models.enums import CheckCategories


class MemoryDBClusterIntransitEncryption(BaseResourceNegativeValueCheck):
    def __init__(self):
        name = "Ensure MemoryDB data is encrypted in transit"
        id = "CKV_AWS_202"
        supported_resources = ("aws_memorydb_cluster",)
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "tls_enabled"

    def get_forbidden_values(self) -> list[Any]:
        return [False]


check = MemoryDBClusterIntransitEncryption()

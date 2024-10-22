from __future__ import annotations

from typing import Any

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.checks.base_check_registry import BaseCheckRegistry


class Registry(BaseCheckRegistry):
    def __init__(self) -> None:
        super().__init__(report_type=CheckType.CLOUDFORMATION)

    def extract_entity_details(self, entity: dict[str, dict[str, Any]]) -> tuple[str, str, dict[str, Any]]:
        resource_name, resource = next(iter(entity.items()))
        resource_type = resource["Type"]
        return resource_type, resource_name, resource

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.checks.base_check import BaseCheck
from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.runner_filter import RunnerFilter

if TYPE_CHECKING:
    from pycep.typing import ParameterAttributes


class Registry(BaseCheckRegistry):
    def __init__(self) -> None:
        self.entity_to_check_map: dict[str, set[str]] = defaultdict(set)

        super().__init__(report_type=CheckType.BICEP)

    def register(self, check: BaseCheck) -> None:
        if self._BaseCheckRegistry__loading_external_checks:  # type:ignore[attr-defined]  # they exist
            RunnerFilter.notify_external_check(check.id)

        for entity in check.supported_entities:
            checks = self.wildcard_checks if self._is_wildcard(entity) else self.checks
            if check.id not in self.entity_to_check_map[entity]:
                checks[entity].append(check)
                self.entity_to_check_map[entity].add(check.id)

        self._BaseCheckRegistry__all_registered_checks.append(check)  # type:ignore[attr-defined]  # they exist

    def extract_entity_details(self, entity: dict[str, ParameterAttributes]) -> tuple[str, str, ParameterAttributes]:  # type:ignore[override]  # it's ok
        param_name, param = next(iter(entity.items()))
        param_type = param["type"]
        return param_type, param_name, param

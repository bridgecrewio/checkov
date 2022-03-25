from __future__ import annotations

from pycep.typing import ResourceAttributes

from checkov.common.checks.base_check import BaseCheck
from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.common.checks_infra.registry import get_graph_checks_registry
from checkov.common.output.report import CheckType
from checkov.runner_filter import RunnerFilter


class Registry(BaseCheckRegistry):
    def __init__(self) -> None:
        self.check_id_to_enitity_map: dict[str, list[str]] = {}

        self.graph_registry = get_graph_checks_registry(CheckType.BICEP)
        self.graph_registry.load_checks()
        self.graph_check_ids = [check.id for check in self.graph_registry.checks]

        super().__init__()

    def register(self, check: BaseCheck) -> None:
        # a copy of the original method to be able to prioritize Bicep styled checks over the ARM equivalent
        if self._BaseCheckRegistry__loading_external_checks:
            RunnerFilter.notify_external_check(check.id)

        # don't add an ARM check, if a Bicep graph check exists for it
        if check.id in self.graph_check_ids:
            return

        # remove the ARM check, if a Bicep check with the same check ID exists
        if check.id in self.check_id_to_enitity_map.keys():
            if check.__module__.split(".")[1] != "bicep":
                return

            entities = self.check_id_to_enitity_map[check.id]
            for entity in entities:
                checks = self.wildcard_checks if self._is_wildcard(entity) else self.checks
                check_idx = next((idx for idx, c in enumerate(checks[entity]) if c.id == check.id), None)
                if check_idx is not None:
                    del checks[entity][check_idx]

            del self.check_id_to_enitity_map[check.id]

        for entity in check.supported_entities:
            checks = self.wildcard_checks if self._is_wildcard(entity) else self.checks
            checks[entity].append(check)
            self.check_id_to_enitity_map.setdefault(check.id, []).append(entity)

        self._BaseCheckRegistry__all_registered_checks.append(check)

    def extract_entity_details(self, entity: dict[str, ResourceAttributes]) -> tuple[str, str, ResourceAttributes]:
        resource_name, resource = next(iter(entity.items()))
        resource_type = resource["type"]
        return resource_type, resource_name, resource

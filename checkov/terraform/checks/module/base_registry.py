from typing import Dict, Any, Tuple

from checkov.common.checks.base_check_registry import BaseCheckRegistry


class Registry(BaseCheckRegistry):
    def __init__(self) -> None:
        super().__init__()

    def extract_entity_details(self, entity: Dict[str, Dict[str, Any]]) -> Tuple[str, str, Dict[str, Any]]:
        module_name, module_configuration = next(iter(entity.items()))
        return "module", module_name, module_configuration

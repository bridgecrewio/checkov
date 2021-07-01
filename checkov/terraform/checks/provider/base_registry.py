from typing import Dict, Any, Tuple

from checkov.common.checks.base_check_registry import BaseCheckRegistry


class Registry(BaseCheckRegistry):
    def extract_entity_details(self, entity: Dict[str, Any]) -> Tuple[str, str, Dict[str, Any]]:
        provider_type = list(entity.keys())[0]
        provider_name = list(entity.keys())[0]
        provider_configuration = entity[provider_name]
        return provider_type, provider_name, provider_configuration

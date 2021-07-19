from typing import Dict, Any, Tuple

from checkov.common.checks.base_check_registry import BaseCheckRegistry


class Registry(BaseCheckRegistry):
    def extract_entity_details(self, entity: Dict[str, Any]) -> Tuple[str, str, Dict[str, Any]]:
        resource_type = list(entity.keys())[0]
        resource_name = list(list(entity.values())[0].keys())[0]
        resource_object = entity[resource_type]
        resource_configuration = resource_object[resource_name]
        return resource_type, resource_name, resource_configuration

from typing import Dict, Any, Tuple, List

from checkov.common.checks.base_check_registry import BaseCheckRegistry


class Registry(BaseCheckRegistry):
    def extract_entity_details(
        self, entity: Dict[str, Dict[str, Dict[str, List[Dict[str, Any]]]]]
    ) -> Tuple[str, str, Dict[str, List[Dict[str, Any]]]]:
        data_type, data_object = next(iter(entity.items()))
        data_name, data_configuration = next(iter(data_object.items()))
        return data_type, data_name, data_configuration

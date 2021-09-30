from typing import Tuple, Dict

from checkov.cloudformation.parser import dict_node
from checkov.common.parsers.node import str_node
from checkov.common.checks.base_check_registry import BaseCheckRegistry


class Registry(BaseCheckRegistry):
    def extract_entity_details(self, entity: Dict[str_node, dict_node]) -> Tuple[str_node, str_node, dict_node]:
        resource_name, resource = next(iter(entity.items()))
        resource_type = resource["Type"]
        return resource_type, resource_name, resource

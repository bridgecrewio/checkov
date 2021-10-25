from typing import Tuple, Dict

from checkov.cloudformation.parser import DictNode
from checkov.common.parsers.node import StrNode
from checkov.common.checks.base_check_registry import BaseCheckRegistry


class Registry(BaseCheckRegistry):
    def extract_entity_details(self, entity: Dict[StrNode, DictNode]) -> Tuple[StrNode, StrNode, DictNode]:
        resource_name, resource = next(iter(entity.items()))
        resource_type = resource["Type"]
        return resource_type, resource_name, resource

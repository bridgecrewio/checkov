from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.terraform.tag_providers import get_resource_tags


class Registry(BaseCheckRegistry):

    def __init__(self):
        super().__init__()

    def extract_entity_details(self, entity):
        resource_type = list(entity.keys())[0]
        resource_name = list(list(entity.values())[0].keys())[0]
        resource_object = entity[resource_type]
        resource_configuration = resource_object[resource_name]
        return resource_type, resource_name, resource_configuration

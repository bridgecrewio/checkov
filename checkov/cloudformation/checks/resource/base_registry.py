from checkov.common.checks.base_check_registry import BaseCheckRegistry


class Registry(BaseCheckRegistry):

    def __init__(self):
        super().__init__()

    def extract_entity_details(self, entity):
        resource_name, resource = next(iter(entity.items()))
        resource_type = resource['Type']
        return resource_type, resource_name, resource

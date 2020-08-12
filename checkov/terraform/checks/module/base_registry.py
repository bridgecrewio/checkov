from checkov.common.checks.base_check_registry import BaseCheckRegistry


class Registry(BaseCheckRegistry):

    def __init__(self):
        super().__init__()

    def extract_entity_details(self, entity):
        module_name = list(entity.keys())[0]
        module_configuration = entity[module_name]
        return "module", module_name, module_configuration


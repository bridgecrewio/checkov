from checkov.common.checks.base_check_registry import BaseCheckRegistry


class Registry(BaseCheckRegistry):

    def __init__(self):
        super().__init__()

    def extract_entity_details(self, entity):
        provider_type = list(entity.keys())[0]
        provider_name = list(entity.keys())[0]
        provider_configuration = entity[provider_name]
        return provider_type, provider_name, provider_configuration


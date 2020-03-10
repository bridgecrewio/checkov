from checkov.common.checks.base_check_registry import BaseCheckRegistry


class Registry(BaseCheckRegistry):

    def __init__(self):
        super().__init__()

    def extract_entity_details(self, entity):
        data_type = list(entity.keys())[0]
        data_name = list(list(entity.values())[0].keys())[0]
        data_object = entity[data_type]
        data_configuration = data_object[data_name]
        return data_type, data_name, data_configuration


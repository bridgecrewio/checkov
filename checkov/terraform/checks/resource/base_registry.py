from checkov.common.checks.base_check_registry import BaseCheckRegistry


class Registry(BaseCheckRegistry):

    def __init__(self):
        super().__init__()

    def scan(self, scanned_file, entity_type, entity_name, entity_configuration, skipped_checks):
        entity_type = list(entity_configuration.keys())[0]
        entity_conf = entity_configuration[entity_type]
        entity_name = list(entity_conf.keys())[0]
        entity_configuration = entity_conf[entity_name]
        results = super().scan(scanned_file, entity_type, entity_name, entity_configuration, skipped_checks)
        return results

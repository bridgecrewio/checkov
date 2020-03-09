from checkov.common.checks.base_check_registry import BaseCheckRegistry


class Registry(BaseCheckRegistry):

    def __init__(self):
        super().__init__()

    def scan(self, scanned_file, entity_type, entity_name, entity_configuration, skipped_checks):
        results = super().scan(scanned_file, entity_type, entity_name, entity_configuration, skipped_checks)
        return results

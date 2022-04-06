from checkov.common.checks.object_registry import Registry as BaseCheckRegistry


class Registry(BaseCheckRegistry):
    def get_key(self, entity_type: str, entity_name: str, check_id: str) -> str:
        return entity_type

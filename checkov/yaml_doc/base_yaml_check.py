from checkov.common.checks.base_check import BaseCheck

from checkov.yaml_doc.registry import registry


class BaseYamlCheck(BaseCheck):
    def __init__(self, name, id, categories, supported_entities, block_type, path=None):
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_entities,
            block_type=block_type,
        )
        self.path = path
        registry.register(self)

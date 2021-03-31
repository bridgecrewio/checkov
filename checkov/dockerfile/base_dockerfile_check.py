from checkov.common.checks.base_check import BaseCheck

from checkov.dockerfile.registry import registry

class BaseDockerfileCheck(BaseCheck):
    def __init__(self, name, id, categories, supported_instructions):
        super().__init__(name=name, id=id, categories=categories, supported_entities=supported_instructions,
                         block_type="dockerfile")
        self.supported_instructions = supported_instructions
        registry.register(self)


from checkov.common.checks.base_check import BaseCheck

from checkov.gitlab.registry import registry


class BaseGitlabCheck(BaseCheck):
    def __init__(self, name, id, categories, supported_entities, block_type, path=None, guideline=None):
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_entities,
            block_type=block_type,
            guideline=guideline,
        )
        self.path = path
        registry.register(self)

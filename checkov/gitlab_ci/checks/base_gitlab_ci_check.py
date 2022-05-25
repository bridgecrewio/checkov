from checkov.common.checks.base_check import BaseCheck
from checkov.common.models.enums import CheckCategories
from checkov.gitlab_ci.checks.registry import registry


class BaseGitlabCICheck(BaseCheck):
    def __init__(self, name, id, supported_entities, block_type, path=None):
        categories = [CheckCategories.SUPPLY_CHAIN]

        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_entities=supported_entities,
            block_type=block_type,
        )
        self.path = path
        registry.register(self)

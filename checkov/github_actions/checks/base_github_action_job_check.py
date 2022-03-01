from checkov.github_actions.checks.base_github_action_check import BaseGithubActionsCheck

from checkov.github_actions.checks.job_registry import registry


class BaseGithubActionsJobCheck(BaseGithubActionsCheck):
    def __init__(self, name, id, block_type, path=None):
        super().__init__(
            name=name,
            id=id,
            supported_entities=["jobs"],
            block_type=block_type,
        )
        self.path = path
        registry.register(self)

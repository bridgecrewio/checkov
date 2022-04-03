#
# Small customisations below to import resource registry and add the 
# resource type to the supported_entities

from checkov.example_runner.checks.base_example_runner_check import BaseExampleRunnerCheck
# The base check required you to import the resource check registry
from checkov.example_runner.checks.job_registry import registry


class BaseExampleRunnerJobCheck(BaseExampleRunnerCheck):
    def __init__(self, name, id, block_type, path=None):
        super().__init__(
            name=name,
            id=id,
            # Set up your runner for the correct resource types
            # This is the same string is you defined in line 20
            # in your runner.py 
            supported_entities=["jobs"],
            block_type=block_type,
        )
        self.path = path
        registry.register(self)

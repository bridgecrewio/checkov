import os

from checkov.common.output.report import CheckType
from checkov.github_actions.checks.job_registry import registry as job_registry
from checkov.yaml_doc.runner import Runner as YamlRunner


class Runner(YamlRunner):
    check_type = CheckType.GITHUB_ACTIONS
    block_type_registries = {
        'jobs': job_registry,
    }

    def __init__(self):
        super().__init__()

    def require_external_checks(self):
        return False

    def import_registry(self):
        return self.block_type_registries['jobs']

    def _parse_file(self, f):
        if ".github/workflows/" in os.path.abspath(f):
            return super()._parse_file(f)

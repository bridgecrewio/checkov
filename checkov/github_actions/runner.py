import os

from checkov.common.output.report import CheckType
from checkov.github_actions.checks.job_registry import registry as job_registry
from checkov.runner_filter import RunnerFilter
from checkov.yaml_doc.runner import Runner as YamlRunner


class Runner(YamlRunner):
    check_type = CheckType.GITHUB_ACTION
    block_type_registries = {
        'jobs': job_registry,
    }

    def __init__(self):
        super().__init__()

    def run(self, root_folder=None, external_checks_dir=None, files=None,
            runner_filter=RunnerFilter(), collect_skip_comments=True):
        report = super().run(root_folder=root_folder, external_checks_dir=external_checks_dir,
                             files=files,
                             runner_filter=runner_filter, collect_skip_comments=collect_skip_comments)
        return report

    def require_external_checks(self):
        return False

    def import_registry(self):
        return self.block_type_registries['jobs']

    def _parse_file(self, f):
        if ".github/workflows/" in os.path.abspath(f):
            return super()._parse_file(f)


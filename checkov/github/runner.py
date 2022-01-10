from checkov.github.dal import Github
from checkov.json_doc.runner import Runner as JsonRunner
from checkov.runner_filter import RunnerFilter


class Runner(JsonRunner):
    check_type = "github_configuration"

    def __init__(self):
        self.github = Github()
        super().__init__()

    def run(self, root_folder=None, external_checks_dir=None, files=None,
            runner_filter=RunnerFilter(), collect_skip_comments=True):
        self.prepare_data()

        report = super().run(root_folder=self.github.github_conf_dir_path, external_checks_dir=external_checks_dir,
                             files=files,
                             runner_filter=runner_filter, collect_skip_comments=collect_skip_comments)
        return report

    def prepare_data(self):
        self.github.persist_all_confs()

    def require_external_checks(self):
        # default json runner require only external checks. Github runner brings build in checks
        return False

    def import_registry(self):
        from checkov.github.registry import registry
        return registry

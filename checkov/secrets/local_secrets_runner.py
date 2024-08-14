# flake8: noqa
# type: ignore

import json
import os

from checkov.main import secrets_runner
from checkov.common.runners.runner_registry import RunnerRegistry
from checkov.runner_filter import RunnerFilter
from checkov.common.bridgecrew.platform_integration import bc_integration


with open(os.environ['LOCAL_SECRETS_POLICIES_JSON']) as secrets_policies_file:
    default_regexes = json.load(secrets_policies_file)
bc_integration.customer_run_config_response = {'secretsPolicies': default_regexes}


def execute():
    runner = secrets_runner(entropy_limit=4)
    # 20 min less in order to finish processing, else put checkov's default (12h - 1200)
    runner_registry = RunnerRegistry(
        '',
        RunnerFilter(
            block_list_secret_scan=[],
            enable_secret_scan_all_files=True,
            enable_git_history_secret_scan=False,
            git_history_last_commit_scanned=None,
            git_history_timeout="checkov_timeout_str",
            checks=['BC_GIT_79']
        ),
        runner
    )

    scan_reports = runner_registry.run(
        root_folder=os.environ["LOCAL_SCANNING_FOLDER"],
        external_checks_dir=list(),
        collect_skip_comments=True)

    print(scan_reports)


if __name__ == "__main__":
    execute()

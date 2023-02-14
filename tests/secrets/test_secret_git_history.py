from __future__ import annotations

import pickle
from unittest import mock

from detect_secrets import SecretsCollection
from git import Commit  # type: ignore

from checkov.secrets.scan_git_history import scan_history
from checkov.secrets.runner import Runner
from checkov.runner_filter import RunnerFilter
from detect_secrets.settings import transient_settings


def mock_git_repo_commits(root_folder: str) -> list[Commit] | None:
    with open('git_history/mock_git_commits.pkl', 'rb') as f:
        mock_repo = pickle.load(f)
    return mock_repo  # type: ignore


@mock.patch('checkov.secrets.git_history_scan.get_commits', mock_git_repo_commits)
def test_scan_git_history() -> None:
    valid_dir_path = "/git_history/test2"

    runner = Runner()
    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    # we have 5 secret but for now the secret runner filter secret from the same file and the same value
    assert len(report.failed_checks) == 3
    assert len(report.parsing_errors) == 0
    assert len(report.passed_checks) == 0
    assert len(report.parsing_errors) == 0
    assert len(report.skipped_checks) == 0


@mock.patch('checkov.secrets.git_history_scan.get_commits', mock_git_repo_commits)
def test_scan_history_secrets() -> None:
    valid_dir_path = "/git_history/test2"
    secrets = SecretsCollection()
    plugins_used = [
        {'name': 'AWSKeyDetector'},
    ]
    with transient_settings({
        # Only run scans with only these plugins.
        'plugins_used': plugins_used
    }) as settings:
        settings.disable_filters(*['detect_secrets.filters.common.is_invalid_file'])
        scan_history(valid_dir_path, secrets)

    assert len(secrets.data) == 5

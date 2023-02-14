from __future__ import annotations

import pickle
from unittest import mock

from git import Commit
from pytest_mock import MockerFixture

from checkov.secrets.runner import Runner
from checkov.runner_filter import RunnerFilter


def mock_git_repo_commits(self, root_folder: str) -> list[Commit] | None:
    with open('git_history/mock_git_commits.pkl', 'rb') as f:
        mock_repo = pickle.load(f)
    return mock_repo  # type: ignore


@mock.patch('checkov.secrets.runner.Runner._get_commits', mock_git_repo_commits)
def test_scan_history_secrets(mocker: MockerFixture) -> None:
    valid_dir_path = "/git_history/test2"
    # secrets = SecretsCollection()
    # scan_history(valid_dir_path, secrets)

    runner = Runner()
    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    assert len(report.failed_checks) == 3
    assert len(report.parsing_errors) == 0
    assert len(report.passed_checks) == 0
    assert len(report.parsing_errors) == 0
    assert len(report.skipped_checks) == 0

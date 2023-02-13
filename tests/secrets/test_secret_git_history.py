import os
from unittest.mock import MagicMock, patch
import git
from pytest_mock import MockerFixture

from checkov.secrets.runner import Runner
from checkov.runner_filter import RunnerFilter


# @patch('git.Repo', MagicMock(spec=git.Repo))
def test_sanity_check_secrets(mocker: MockerFixture, mock_git_repo):
    mocker.patch('checkov.secrets.runner.git.Repo', return_value=mock_git_repo)
    # with patch('git.Repo', MagicMock(spec=git.Repo)):
    #     git.Repo.return_value = mock_git_repo

    current_dir = os.path.dirname(os.path.realpath(__file__))
    valid_dir_path = current_dir + "/git_history/test2"
    runner = Runner()
    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    assert len(report.failed_checks) == 2
    assert len(report.parsing_errors) == 0
    assert len(report.passed_checks) == 0
    assert len(report.parsing_errors) == 0
    assert len(report.skipped_checks) == 0

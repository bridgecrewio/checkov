from __future__ import annotations

import os
from typing import List
from unittest import mock
from pathlib import Path
import shutil
from copy import deepcopy

from detect_secrets import SecretsCollection
from detect_secrets.core.potential_secret import PotentialSecret
from detect_secrets.settings import transient_settings
from pytest_mock import MockerFixture

from checkov.secrets.git_history_store import GitHistorySecretStore
from checkov.secrets.git_types import Commit, CommitMetadata
from checkov.secrets.runner import Runner
from checkov.runner_filter import RunnerFilter
from checkov.common.output.secrets_record import COMMIT_REMOVED_STR, COMMIT_ADDED_STR

from tests.secrets.git_history.test_utils import mock_git_repo_commits1, mock_git_repo_commits2, mock_git_repo_commits3, \
    mock_set_repo, mock_get_first_commit, mock_get_first_empty_commit, mock_run_forever, mock_get_commits, \
    mock_get_commits_diff_iter1, mock_get_commits_diff_iter2, mock_get_commits_diff_iter3, \
    mock_get_commits_diff_remove_file, mock_get_commits_diff_rename_file, mock_get_commits_diff_iter_keyword_combinator, \
    mock_get_commits_diff_iter_modify_and_rename_file, mock_get_commits_diff_iter_remove_file_with_two_equal_secret, \
    mock_get_commits_diff_iter_remove_file_with_two_secret, mock_get_commits_diff_iter_multiline_json, \
    mock_get_commits_diff_iter_multiline_terraform, mock_get_commits_diff_iter_multiline_yml


@mock.patch.dict(os.environ, {"GIT_HISTORY_PRODUCER_CONSUMER": "1"})
@mock.patch('checkov.secrets.scan_git_history.get_commits', mock_get_commits)
@mock.patch('checkov.secrets.scan_git_history.get_commits_diff_iter', mock_get_commits_diff_iter1)
@mock.patch('checkov.secrets.scan_git_history.set_repo', mock_set_repo)
@mock.patch('checkov.secrets.scan_git_history.get_first_commit', mock_get_first_commit)
def test_scan_git_history() -> None:
    valid_dir_path = "test"

    runner = Runner()
    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    assert len(report.failed_checks) == 6
    assert len(report.parsing_errors) == 0
    assert len(report.passed_checks) == 0
    assert len(report.parsing_errors) == 0
    assert len(report.skipped_checks) == 0
    for failed_check in report.failed_checks:
        assert failed_check.added_commit_hash or failed_check.removed_commit_hash
        if failed_check.removed_commit_hash:
            assert failed_check.removed_date
        assert failed_check.added_by
        assert failed_check.added_date


@mock.patch.dict(os.environ, {"GIT_HISTORY_PRODUCER_CONSUMER": "1"})
@mock.patch('checkov.secrets.scan_git_history.get_commits', mock_get_commits)
@mock.patch('checkov.secrets.scan_git_history.get_commits_diff_iter', mock_get_commits_diff_iter1)
@mock.patch('checkov.secrets.scan_git_history.set_repo', mock_set_repo)
@mock.patch('checkov.secrets.scan_git_history.get_first_commit', mock_get_first_commit)
def test_scan_history_secrets() -> None:
    valid_dir_path = "test"
    secrets = SecretsCollection()
    plugins_used = [
        {'name': 'AWSKeyDetector'},
    ]
    from checkov.secrets.scan_git_history import GitHistoryScanner

    with transient_settings({
        # Only run scans with only these plugins.
        'plugins_used': plugins_used
    }) as settings:
        settings.disable_filters(*['detect_secrets.filters.common.is_invalid_file'])
        GitHistoryScanner(valid_dir_path, secrets).scan_history()
    assert len(secrets.data) == 3


@mock.patch.dict(os.environ, {"GIT_HISTORY_PRODUCER_CONSUMER": "1"})
@mock.patch('checkov.secrets.scan_git_history.get_commits', mock_get_commits)
@mock.patch('checkov.secrets.scan_git_history.get_commits_diff_iter', mock_get_commits_diff_iter2)
@mock.patch('checkov.secrets.scan_git_history.set_repo', mock_set_repo)
@mock.patch('checkov.secrets.scan_git_history.get_first_commit', mock_get_first_commit)
def test_scan_git_history_merge_added_removed() -> None:
    """
    add, move, remove, add, move = secret with the first added_commit_hash and not removed_commit_hash
    """
    valid_dir_path = "test"

    runner = Runner()
    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    assert len(report.failed_checks) == 4
    for failed_check in report.failed_checks:
        assert failed_check.removed_commit_hash == ''
        assert failed_check.removed_date == ''
        assert failed_check.added_commit_hash == '11e59e4e578c6ebcb48aae1e5e078a54c62920eb' or failed_check.added_commit_hash == 'c9b3268e15eb20fd406b9077a4c45875086d6c1b'
        assert failed_check.added_by
        assert failed_check.added_date


@mock.patch.dict(os.environ, {"GIT_HISTORY_PRODUCER_CONSUMER": "1"})
@mock.patch('checkov.secrets.scan_git_history.get_commits', mock_get_commits)
@mock.patch('checkov.secrets.scan_git_history.get_commits_diff_iter', mock_get_commits_diff_iter2)
@mock.patch('checkov.secrets.scan_git_history.set_repo', mock_set_repo)
@mock.patch('checkov.secrets.scan_git_history.get_first_commit', mock_get_first_commit)
def test_scan_history_secrets_merge_added_removed() -> None:
    valid_dir_path = "test"
    secrets = SecretsCollection()
    plugins_used = [
        {'name': 'AWSKeyDetector'},
    ]
    from checkov.secrets.scan_git_history import GitHistoryScanner

    with transient_settings({
        # Only run scans with only these plugins.
        'plugins_used': plugins_used
    }) as settings:
        settings.disable_filters(*['detect_secrets.filters.common.is_invalid_file'])
        GitHistoryScanner(valid_dir_path, secrets).scan_history()
    assert len(secrets.data) == 1


@mock.patch.dict(os.environ, {"GIT_HISTORY_PRODUCER_CONSUMER": "1"})
@mock.patch('checkov.secrets.scan_git_history.get_commits', mock_get_commits)
@mock.patch('checkov.secrets.scan_git_history.get_commits_diff_iter', mock_get_commits_diff_iter3)
@mock.patch('checkov.secrets.scan_git_history.set_repo', mock_set_repo)
@mock.patch('checkov.secrets.scan_git_history.get_first_commit', mock_get_first_commit)
def test_scan_git_history_merge_added_removed2() -> None:
    """
        add, move, add, remove one = 2 secret one with removed_commit_hash && added_commit_hash
        and one with only added_commit_hash
    """
    valid_dir_path = "/Users/lshindelman/development/test2"

    runner = Runner()
    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    assert len(report.failed_checks) == 5
    assert ((report.failed_checks[0].removed_commit_hash == '697308e61171e33224757e620aaf67b1a877c99d'
             and report.failed_checks[0].removed_date
             and report.failed_checks[1].removed_commit_hash == '')
            or (report.failed_checks[1].removed_commit_hash == '697308e61171e33224757e620aaf67b1a877c99d'
                and report.failed_checks[1].removed_date
                and report.failed_checks[0].removed_commit_hash == ''))
    assert report.failed_checks[0].added_by and report.failed_checks[0].added_date
    assert report.failed_checks[1].added_by and report.failed_checks[1].added_date
    assert ((report.failed_checks[0].added_commit_hash == '900b1e8f6f336a92e8f5fca3babca764e32c3b3d'
             and report.failed_checks[1].added_commit_hash == '3c8cb7eedb3986308c96713fc65b006adcf3bc44')
            or (report.failed_checks[1].added_commit_hash == '900b1e8f6f336a92e8f5fca3babca764e32c3b3d'
                and report.failed_checks[0].added_commit_hash == '3c8cb7eedb3986308c96713fc65b006adcf3bc44'))
    # print testing
    assert_for_commit_str(report.failed_checks[0].to_string() + report.failed_checks[1].to_string(),
                          commit_type=COMMIT_REMOVED_STR,
                          commit_hash='697308e61171e33224757e620aaf67b1a877c99d')
    assert_for_commit_str(report.failed_checks[0].to_string() + report.failed_checks[1].to_string(),
                          commit_type=COMMIT_ADDED_STR,
                          commit_hash='3c8cb7eedb3986308c96713fc65b006adcf3bc44')
    assert_for_commit_str(report.failed_checks[0].to_string() + report.failed_checks[1].to_string(),
                          commit_type=COMMIT_ADDED_STR,
                          commit_hash='900b1e8f6f336a92e8f5fca3babca764e32c3b3d')


# this test is too flaky !
# @pytest.mark.filterwarnings("error")  # otherwise pytest sometimes suppresses the raised Timeout Exception
# @mock.patch('checkov.secrets.scan_git_history.GitHistoryScanner._get_commits_diff', mock_git_repo_commits_too_much)
# @mock.patch('checkov.secrets.scan_git_history.set_repo', mock_set_repo)
# @mock.patch('checkov.secrets.scan_git_history.get_first_commit', mock_get_first_commit)
# def test_scan_history_secrets_timeout() -> None:
#     """
#     add way too many cases to check in 1 second
#     """
#     valid_dir_path = "test"
#     secrets = SecretsCollection()
#     plugins_used = [
#         {'name': 'AWSKeyDetector'},
#     ]
#     from checkov.secrets.scan_git_history import GitHistoryScanner
#
#     with transient_settings({
#         # Only run scans with only these plugins.
#         'plugins_used': plugins_used
#     }) as settings:
#         settings.disable_filters(*['detect_secrets.filters.common.is_invalid_file'])
#         finished = GitHistoryScanner(valid_dir_path, secrets, None, 1).scan_history()
#
#     assert finished is False

@mock.patch.dict(os.environ, {"GIT_HISTORY_PRODUCER_CONSUMER": "1"})
@mock.patch('checkov.secrets.scan_git_history.get_commits', mock_get_commits)
@mock.patch('checkov.secrets.scan_git_history.get_commits_diff_iter', mock_run_forever)
def test_scan_history_secrets_timeout() -> None:
    """
    add way too many cases to check in 1 second
    """
    valid_dir_path = "test"
    secrets = SecretsCollection()
    plugins_used = [
        {'name': 'AWSKeyDetector'},
    ]
    from checkov.secrets.scan_git_history import GitHistoryScanner

    with transient_settings({
        # Only run scans with only these plugins.
        'plugins_used': plugins_used
    }) as settings:
        settings.disable_filters(*['detect_secrets.filters.common.is_invalid_file'])
        finished = GitHistoryScanner(valid_dir_path, secrets, None, 1).scan_history()

    assert finished is False


@mock.patch.dict(os.environ, {"GIT_HISTORY_PRODUCER_CONSUMER": "1"})
@mock.patch('checkov.secrets.scan_git_history.get_commits', mock_get_commits)
@mock.patch('checkov.secrets.scan_git_history.get_commits_diff_iter', mock_get_commits_diff_remove_file)
@mock.patch('checkov.secrets.scan_git_history.set_repo', mock_set_repo)
@mock.patch('checkov.secrets.scan_git_history.get_first_commit', mock_get_first_commit)
def test_scan_git_history_remove_file() -> None:
    valid_dir_path = "remove_file"

    runner = Runner()
    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    assert len(report.failed_checks) == 4
    assert report.failed_checks[0].removed_commit_hash == '4bd08cd0b2874025ce32d0b1e9cd84ca20d59ce1'
    assert report.failed_checks[0].removed_date
    assert report.failed_checks[0].added_commit_hash == '63342dbee285973a37770bbb1ff4258a3184901e'
    assert report.failed_checks[0].added_by and report.failed_checks[0].added_date
    assert report.failed_checks[0].removed_date


@mock.patch.dict(os.environ, {"GIT_HISTORY_PRODUCER_CONSUMER": "1"})
@mock.patch('checkov.secrets.scan_git_history.get_commits', mock_get_commits)
@mock.patch('checkov.secrets.scan_git_history.get_commits_diff_iter', mock_get_commits_diff_rename_file)
@mock.patch('checkov.secrets.scan_git_history.set_repo', mock_set_repo)
@mock.patch('checkov.secrets.scan_git_history.get_first_commit', mock_get_first_commit)
def test_scan_git_history_rename_file() -> None:
    valid_dir_path = "/test/git/history/rename/file"

    runner = Runner()
    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    assert len(report.failed_checks) == 5
    assert (report.failed_checks[0].removed_commit_hash == '' and report.failed_checks[0].removed_date == '' and
            report.failed_checks[0].added_commit_hash == '2e1a500e688990e065fc6f1202bc64ed0ba53027')
    assert (report.failed_checks[1].removed_commit_hash == '2e1a500e688990e065fc6f1202bc64ed0ba53027' and
            report.failed_checks[1].removed_date == '2022-12-14T16:32:13+00:00' and
            report.failed_checks[1].added_commit_hash == 'adef7360b86c62666f0a70521214220763b9c593')


@mock.patch.dict(os.environ, {"GIT_HISTORY_PRODUCER_CONSUMER": "1"})
@mock.patch('checkov.secrets.scan_git_history.get_commits', mock_get_commits)
@mock.patch('checkov.secrets.scan_git_history.get_commits_diff_iter',
            mock_get_commits_diff_iter_modify_and_rename_file)
@mock.patch('checkov.secrets.scan_git_history.set_repo', mock_set_repo)
@mock.patch('checkov.secrets.scan_git_history.get_first_commit', mock_get_first_commit)
def test_scan_git_history_modify_and_rename_file() -> None:
    valid_dir_path = "test_scan_git_history_modify_and_rename_file"

    runner = Runner()
    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    assert len(report.failed_checks) == 4
    assert report.failed_checks[0].added_commit_hash == '62da8e5e04ec5c3a474467e9012bf3427cff0407'
    assert report.failed_checks[0].added_by and report.failed_checks[0].added_date
    assert report.failed_checks[0].removed_commit_hash == '61ee79aea3d151a40c8e054295f330d233eaf7d5'
    assert report.failed_checks[0].removed_date


@mock.patch.dict(os.environ, {"GIT_HISTORY_PRODUCER_CONSUMER": "1"})
@mock.patch('checkov.secrets.scan_git_history.get_commits', mock_get_commits)
@mock.patch('checkov.secrets.scan_git_history.get_commits_diff_iter',
            mock_get_commits_diff_iter_remove_file_with_two_equal_secret)
@mock.patch('checkov.secrets.scan_git_history.set_repo', mock_set_repo)
@mock.patch('checkov.secrets.scan_git_history.get_first_commit', mock_get_first_empty_commit)
def test_scan_git_history_rename_file_with_two_equal_secrets() -> None:
    valid_dir_path = "test_scan_git_history_rename_file_with_two_equal_secrets"
    runner = Runner()
    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    assert len(report.failed_checks) == 2

    assert report.failed_checks[0].removed_commit_hash == report.failed_checks[1].removed_commit_hash
    assert report.failed_checks[1].removed_commit_hash
    assert report.failed_checks[0].removed_date and report.failed_checks[0].removed_date == report.failed_checks[
        1].removed_date


@mock.patch.dict(os.environ, {"GIT_HISTORY_PRODUCER_CONSUMER": "1"})
@mock.patch('checkov.secrets.scan_git_history.get_commits', mock_get_commits)
@mock.patch('checkov.secrets.scan_git_history.get_commits_diff_iter',
            mock_get_commits_diff_iter_remove_file_with_two_secret)
@mock.patch('checkov.secrets.scan_git_history.set_repo', mock_set_repo)
@mock.patch('checkov.secrets.scan_git_history.get_first_commit', mock_get_first_empty_commit)
def test_scan_git_history_rename_file_with_two_secrets() -> None:
    valid_dir_path = "test_scan_git_history_rename_file_with_two_secrets"
    runner = Runner()
    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    assert len(report.failed_checks) == 2
    report.failed_checks[0].removed_commit_hash == report.failed_checks[1].removed_commit_hash
    assert report.failed_checks[1].removed_commit_hash
    assert report.failed_checks[0].removed_date and report.failed_checks[0].removed_date == report.failed_checks[
        1].removed_date


def assert_for_commit_str(report_str: List[str], commit_type: str, commit_hash: str, found: bool = True) -> None:
    to_find = f'; {commit_type}: {commit_hash}'
    assert (to_find in report_str) == found


# added all file scenarios from multiline tests
@mock.patch.dict(os.environ, {"GIT_HISTORY_PRODUCER_CONSUMER": "1"})
@mock.patch('checkov.secrets.scan_git_history.get_commits', mock_get_commits)
@mock.patch('checkov.secrets.scan_git_history.get_commits_diff_iter',
            mock_get_commits_diff_iter_multiline_json)
@mock.patch('checkov.secrets.scan_git_history.set_repo', mock_set_repo)
@mock.patch('checkov.secrets.scan_git_history.get_first_commit', mock_get_first_empty_commit)
def test_scan_git_history_multiline_keyword_json() -> None:
    valid_dir_path = "multiline_keyword_json"

    runner = Runner()
    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    assert len(report.failed_checks) == 5
    assert report.parsing_errors == []
    assert report.passed_checks == []
    assert report.skipped_checks == []


@mock.patch.dict(os.environ, {"GIT_HISTORY_PRODUCER_CONSUMER": "1"})
@mock.patch('checkov.secrets.scan_git_history.get_commits', mock_get_commits)
@mock.patch('checkov.secrets.scan_git_history.get_commits_diff_iter', mock_get_commits_diff_iter_multiline_terraform)
@mock.patch('checkov.secrets.scan_git_history.set_repo', mock_set_repo)
@mock.patch('checkov.secrets.scan_git_history.get_first_commit', mock_get_first_empty_commit)
def test_scan_git_history_multiline_keyword_terraform() -> None:
    valid_dir_path = "mock_git_repo_multiline_terraform"

    runner = Runner()
    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    #  then
    failing_resources = {
        "6bee3eb2f69e06095395ae1d54c810c3a2a99841:9ed4f1457a9c27dd868c1f21276c6d7098d2bacf",
        "6bee3eb2f69e06095395ae1d54c810c3a2a99841:5db2fafebcfed9b4c9ffc570c46ef2ca94a3881a",
        "6bee3eb2f69e06095395ae1d54c810c3a2a99841:ac236b0474a9a702f99dbe244a14548783ace5c5",
        "6bee3eb2f69e06095395ae1d54c810c3a2a99841:06af723e58378574456be0b4c41a89194aaed0c3",
        "6bee3eb2f69e06095395ae1d54c810c3a2a99841:dcbf46de362e1b6942054b89ee293984e9a8a40a",
    }

    failed_check_resources = {c.resource for c in report.failed_checks}

    assert len(report.failed_checks) == len(failing_resources)
    assert report.parsing_errors == []
    assert report.passed_checks == []
    assert report.skipped_checks == []
    assert failing_resources == failed_check_resources


@mock.patch.dict(os.environ, {"GIT_HISTORY_PRODUCER_CONSUMER": "1"})
@mock.patch('checkov.secrets.scan_git_history.get_commits', mock_get_commits)
@mock.patch('checkov.secrets.scan_git_history.get_commits_diff_iter', mock_get_commits_diff_iter_multiline_yml)
@mock.patch('checkov.secrets.scan_git_history.set_repo', mock_set_repo)
@mock.patch('checkov.secrets.scan_git_history.get_first_commit', mock_get_first_commit)
def test_scan_git_history_multiline_keyword_yml() -> None:
    valid_dir_path = "mock_git_repo_multiline_yml"
    runner = Runner()

    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    assert len(report.failed_checks) == 8
    assert report.parsing_errors == []
    assert report.passed_checks == []
    assert report.skipped_checks == []


@mock.patch.dict(os.environ, {"GIT_HISTORY_PRODUCER_CONSUMER": "1"})
@mock.patch('checkov.secrets.scan_git_history.get_commits', mock_get_commits)
def test_scan_git_history_full_vs_partial(mocker: MockerFixture) -> None:
    # this takes the 3 mock commits and run _test_it on them
    commits_func = [mock_git_repo_commits1('', ''), mock_git_repo_commits2('', ''), mock_git_repo_commits3('', '')]
    all([_test_it(mocker, commits) for commits in commits_func])


def _test_it(mocker: MockerFixture, all_commits: List[Commit]) -> bool:
    """
    this test tries to run a full scan over 5 commits,
    then run two separate runs over the first 2 and the last 3 (the second will give the secret store to the third)
    then compares the results from run 1 to the last run
    """
    valid_dir_path = "test"
    mocker.patch(
        "checkov.secrets.scan_git_history.get_commits_diff_iter",
        return_value=all_commits,
    )
    runner = Runner()
    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    sec_store = runner.get_history_secret_store()
    # assert len(report.failed_checks) == 3
    for failed_check in report.failed_checks:
        assert failed_check.added_commit_hash or failed_check.removed_commit_hash
        assert failed_check.added_by and failed_check.added_date

    mocker.patch(
        "checkov.secrets.scan_git_history.get_commits_diff_iter", return_value=all_commits[0:1])
    runner2 = Runner()
    report2 = runner2.run(root_folder=valid_dir_path, external_checks_dir=None,
                          runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    # assert len(report2.failed_checks) == 1
    sec_store2 = runner2.get_history_secret_store()
    sec_store2_dc = deepcopy(sec_store2)

    mocker.patch(
        "checkov.secrets.scan_git_history.get_commits_diff_iter", return_value=all_commits[2:5])
    runner3 = Runner()
    runner3.set_history_secret_store(sec_store2_dc)
    report3 = runner3.run(root_folder=valid_dir_path, external_checks_dir=None,
                          runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    sec_store3 = runner3.get_history_secret_store()
    assert len(report3.failed_checks) == len(report.failed_checks)
    for failed_check in report3.failed_checks:
        assert failed_check.added_commit_hash or failed_check.removed_commit_hash
        assert failed_check.added_by and failed_check.added_date
    # check the secret store to have the same results
    assert len(sec_store) == len(sec_store3)
    for k1, k3 in zip(sec_store, sec_store3):
        assert k1 == k3
        assert sec_store[k1][0].get('added_commit_hash') == sec_store3[k3][0].get('added_commit_hash')
    return True


def test_scan_git_history_real_repo() -> None:
    """
    runs over a real repo inside the resource dir and takes the results
    """

    dir_path = Path(__file__).parent / 'git_history/testing_repo'
    git_conf_dir = dir_path / 'git_to_change'
    tmp_git_conf_dir = dir_path / '.git'
    shutil.rmtree(tmp_git_conf_dir, ignore_errors=True)  # make sure no left overs from prev run
    shutil.copytree(git_conf_dir, tmp_git_conf_dir)

    runner = Runner()
    report = runner.run(root_folder=str(dir_path), external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    assert len(report.failed_checks) == 2
    assert report.failed_checks[0].added_commit_hash and not report.failed_checks[0].removed_commit_hash
    assert report.failed_checks[0].added_date and not report.failed_checks[0].removed_date
    assert report.failed_checks[1].added_commit_hash and report.failed_checks[1].removed_commit_hash and \
           report.failed_checks[1].removed_date
    shutil.rmtree(tmp_git_conf_dir)  # just for cleaning


@mock.patch.dict(os.environ, {"GIT_HISTORY_PRODUCER_CONSUMER": "1"})
@mock.patch('checkov.secrets.scan_git_history.get_commits', mock_get_commits)
@mock.patch("checkov.secrets.scan_git_history.get_commits_diff_iter", mock_get_commits_diff_iter_keyword_combinator)
@mock.patch('checkov.secrets.scan_git_history.set_repo', mock_set_repo)
@mock.patch('checkov.secrets.scan_git_history.get_first_commit', mock_get_first_commit)
def test_git_history_plugin() -> None:
    valid_dir_path = "test"
    runner = Runner()
    report = runner.run(root_folder=str(valid_dir_path), external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], enable_git_history_secret_scan=True))
    assert len(report.failed_checks) == 4
    check = report.failed_checks[0]
    assert check.added_commit_hash
    assert check.check_name == 'Base64 High Entropy String'


@mock.patch.dict(os.environ, {"GIT_HISTORY_PRODUCER_CONSUMER": "1"})
@mock.patch('checkov.secrets.scan_git_history.get_commits', mock_get_commits)
@mock.patch("checkov.secrets.scan_git_history.get_commits_diff_iter", lambda a, b, c, d: [])
@mock.patch("checkov.secrets.scan_git_history.set_repo", mock_set_repo)
@mock.patch("checkov.secrets.scan_git_history.get_first_commit", mock_get_first_commit)
def test_scan_history_secrets_with_history_store_and_no_new_commit() -> None:
    # given
    root_folder = "test"
    secrets = SecretsCollection()
    plugins_used = [
        {"name": "AWSKeyDetector"},
    ]

    file_name = "Dockerfile"
    file_results = [
        PotentialSecret(
            type="AWS Access Key",
            filename=file_name,
            secret="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            line_number=7,
            is_added=True,
            is_removed=False,
        )
    ]
    commit = Commit(
        metadata=CommitMetadata(
            commit_hash="8a21fa691e17907afee57e93b7820c5943b12746",
            committer="Momo",
            committed_datetime="2022-12-24T01:02:03+00:00",
        ),
        files={
            "Dockerfile": 'diff --git a/Dockerfile b/Dockerfile\nindex 0000..0000 0000\n--- a/Dockerfile\n+++ b/Dockerfile\n@@ -4,6 +4,8 @@ FROM public.ecr.aws/lambda/python:3.9\n \n ENV PIP_ENV_VERSION="2022.1.8"\n \n+ENV AWS_ACCESS_KEY_ID="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"\n+\n COPY Pipfile Pipfile.lock ./\n \n RUN pip install pipenv==${PIP_ENV_VERSION} \\\n'
        },
    )

    history_store = GitHistorySecretStore()
    history_store.set_secret_map(file_results=file_results, file_name=file_name, commit=commit)

    # when
    from checkov.secrets.scan_git_history import GitHistoryScanner

    with transient_settings(
            {
                # Only run scans with only these plugins.
                "plugins_used": plugins_used
            }
    ) as settings:
        settings.disable_filters(*["detect_secrets.filters.common.is_invalid_file"])
        GitHistoryScanner(root_folder=root_folder, secrets=secrets, history_store=history_store).scan_history()

    # then
    assert len(secrets.data) == 1

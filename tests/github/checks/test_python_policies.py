from __future__ import annotations

from pathlib import Path

import pytest
from time_machine import travel

from checkov.github.runner import Runner
from checkov.runner_filter import RunnerFilter
from tests.common.graph.checks.test_yaml_policies_base import load_yaml_data

BASE_DIR = Path(__file__).parent
CHECK_ID_MAP: "dict[str, str]" = {}  # will be filled via setup()


def test_GithubBranchDisallowDeletions():
    run_check(base_path=BASE_DIR / "branch_security", check="GithubBranchDisallowDeletions")


def test_GithubBranchDismissStaleReviews():
    run_check(base_path=BASE_DIR / "branch_security", check="GithubBranchDismissStaleReviews")


def test_GithubBranchDismissalRestrictions():
    run_check(base_path=BASE_DIR / "branch_security", check="GithubBranchDismissalRestrictions")


def test_GithubBranchRequireCodeOwnerReviews():
    run_check(base_path=BASE_DIR / "branch_security", check="GithubBranchRequireCodeOwnerReviews")


def test_GithubBranchRequireConversationResolution():
    run_check(base_path=BASE_DIR / "branch_security", check="GithubBranchRequireConversationResolution")


def test_GithubBranchRequirePushRestrictions():
    run_check(base_path=BASE_DIR / "branch_security", check="GithubBranchRequirePushRestrictions")


def test_GithubBranchRequireStatusChecks():
    run_check(base_path=BASE_DIR / "branch_security", check="GithubBranchRequireStatusChecks")


def test_GithubRequire2Approvals():
    run_check(base_path=BASE_DIR / "branch_security", check="GithubRequire2Approvals")


@travel("2022-12-05")
def test_GithubDisallowInactiveBranch60Days():
    run_check(base_path=BASE_DIR / "branch_security", check="GithubDisallowInactiveBranch60Days")


def test_GithubRequireUpdatedBranch():
    run_check(base_path=BASE_DIR / "branch_security", check="GithubRequireUpdatedBranch")


def test_GithubPublicRepositoryCreationIsLimited():
    run_check(base_path=BASE_DIR / "repo_management", check="GithubPublicRepositoryCreationIsLimited")


def test_GithubInternalRepositoryCreationIsLimited():
    run_check(base_path=BASE_DIR / "repo_management", check="GithubInternalRepositoryCreationIsLimited")


def test_GithubPrivateRepositoryCreationIsLimited():
    run_check(base_path=BASE_DIR / "repo_management", check="GithubPrivateRepositoryCreationIsLimited")


def test_GithubMinimumAdminsInOrganization():
    run_check(base_path=BASE_DIR / "contribution_access", check="GithubMinimumAdminsInOrganization")


def test_GithubRequireStrictBasePermissionsRepository():
    run_check(base_path=BASE_DIR / "contribution_access", check="GithubRequireStrictBasePermissionsRepository")


def test_GithubRequireOrganizationIsVerified():
    run_check(base_path=BASE_DIR / "contribution_access", check="GithubRequireOrganizationIsVerified")


@pytest.fixture(autouse=True)
def setup():
    global CHECK_ID_MAP
    runner = Runner()
    registry = runner.import_registry()
    CHECK_ID_MAP = {check.__class__.__name__: check.id for entity, check in registry.all_checks()}


def run_check(base_path: Path, check: str) -> None:
    # set path where to find test files
    test_dir_path = base_path / check

    # setup GitHub configuration runner
    runner = Runner()
    runner.github.github_conf_dir_path = str(test_dir_path)

    # run actual check
    report = runner.run(runner_filter=RunnerFilter(checks=CHECK_ID_MAP[check]))

    # get actual results
    summary = report.get_summary()
    passed_checks = {check.file_path.lstrip("/") for check in report.passed_checks}
    failed_checks = {check.file_path.lstrip("/") for check in report.failed_checks}

    # get expected results
    expected = load_yaml_data(dir_path=test_dir_path, source_file_name="expected.yaml")

    # make sure it is a dict
    assert isinstance(expected, dict)

    expected_to_pass = expected.get("pass") or []
    expected_to_fail = expected.get("fail") or []

    # check, if results are correct
    assert summary["passed"] == len(expected_to_pass)
    assert summary["failed"] == len(expected_to_fail)
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0

    assert passed_checks == set(expected_to_pass)
    assert failed_checks == set(expected_to_fail)

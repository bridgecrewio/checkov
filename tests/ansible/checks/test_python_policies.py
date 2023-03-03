from __future__ import annotations

from pathlib import Path

import pytest

from checkov.ansible.runner import Runner
from checkov.runner_filter import RunnerFilter
from tests.common.graph.checks.test_yaml_policies_base import load_yaml_data

BASE_DIR = Path(__file__).parent
CHECK_ID_MAP: "dict[str, str]" = {}  # will be filled via setup()


# Builtin module checks
def test_GetUrlValidateCerts():
    run_check(base_path=BASE_DIR / "task/builtin", check="GetUrlValidateCerts")


def test_UriValidateCerts():
    run_check(base_path=BASE_DIR / "task/builtin", check="UriValidateCerts")


def test_YumSslVerify():
    run_check(base_path=BASE_DIR / "task/builtin", check="YumSslVerify")


def test_YumValidateCerts():
    run_check(base_path=BASE_DIR / "task/builtin", check="YumValidateCerts")


def test_AptAllowUnauthenticated():
    run_check(base_path=BASE_DIR / "task/builtin", check="AptAllowUnauthenticated")


def test_AptForce():
    run_check(base_path=BASE_DIR / "task/builtin", check="AptForce")


# AWS module checks
def test_EC2EBSOptimized():
    run_check(base_path=BASE_DIR / "task/aws", check="EC2EBSOptimized")


def test_EC2PublicIP():
    run_check(base_path=BASE_DIR / "task/aws", check="EC2PublicIP")


@pytest.fixture(autouse=True)
def setup():
    global CHECK_ID_MAP
    registry = Runner().import_registry()
    CHECK_ID_MAP = {check.__class__.__name__: check.id for entity, check in registry.all_checks()}


def run_check(base_path: Path, check: str) -> None:
    # set path where to find test files
    test_dir_path = base_path / check

    # setup Ansible runner
    runner = Runner()

    # run actual check
    report = runner.run(root_folder=str(test_dir_path), runner_filter=RunnerFilter(checks=CHECK_ID_MAP[check]))

    # get actual results
    summary = report.get_summary()
    passed_checks = {check.resource for check in report.passed_checks}
    failed_checks = {check.resource for check in report.failed_checks}

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

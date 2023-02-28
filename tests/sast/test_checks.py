from __future__ import annotations

import os
import pathlib
from pathlib import Path

import pytest

from checkov.sast.runner import Runner
from checkov.sast.checks_infra.registry import registry
from checkov.runner_filter import RunnerFilter
from tests.common.graph.checks.test_yaml_policies_base import load_yaml_data, get_expected_results_by_file_name

BASE_DIR = Path(__file__).parent / 'checks'
CHECK_ID_MAP: "dict[str, str]" = {}  # will be filled via setup()


def test_ChmodPermissiveMask():
    run_check(lang="python", check="ChmodPermissiveMask")


def test_WildcardNeutralizationHandling():
    run_check(lang="python", check="WildcardNeutralizationHandling")


def test_SuperuserPort():
    run_check(lang="python", check="SuperuserPort")


def test_SpecialElementsSQLNeutralization():
    run_check(lang="python", check="SpecialElementsSQLNeutralization")


def test_PubliclyExposedServer():
    run_check(lang="python", check="PubliclyExposedServer")


def test_InputNeutralizationHandling():
    run_check(lang="python", check="InputNeutralizationHandling")


def test_ExecUsage():
    run_check(lang="python", check="ExecUsage")


def test_HardcodedTempDir():
    run_check(lang="python", check="HardcodedTempDir")


def test_HardcodedPassword():
    run_check(lang="python", check="HardcodedPassword")


def test_ExceptionalConditionsHandling():
    run_check(lang="python", check="ExceptionalConditionsHandling")


def test_EncryptionKeySize():
    run_check(lang="python", check="EncryptionKeySize")


def test_DataIntegrityInTransmition():
    run_check(lang="java", check="DataIntegrityInTransmition")


@pytest.fixture(autouse=True)
def setup():
    global CHECK_ID_MAP
    runner_filter = RunnerFilter(framework=['sast'])
    registry.set_runner_filter(runner_filter=runner_filter)
    registry.load_rules(runner_filter.sast_languages)
    CHECK_ID_MAP = {check['metadata']['check_file'].split('.')[0]: check['id'] for check in registry.rules}


def run_check(lang: str, check: str) -> None:
    # set path where to find test files
    test_dir_path = BASE_DIR / lang / check

    # setup sast runner
    runner = Runner()
    runner.registry.temp_semgrep_rules_path = os.path.join(pathlib.Path(__file__).parent.resolve(),
                                                           f'test_{check}_temp_rules.yaml')

    cur_dir = pathlib.Path(__file__).parent.resolve()
    test_files_dir = os.path.join(cur_dir, 'source_code', lang, check)
    test_dir = os.path.join(cur_dir, 'checks')

    # run actual check
    reports = runner.run(test_files_dir, runner_filter=RunnerFilter(framework=['sast'], checks=CHECK_ID_MAP[check]))

    # get actual results
    assert len(reports) == 1
    report = reports[0]
    summary = report.get_summary()
    failed_checks = {check.file_path.lstrip("/") for check in report.failed_checks}

    # get expected results
    expected_to_fail, _ = get_expected_results_by_file_name(test_dir=test_files_dir)

    # check, if results are correct
    assert summary["failed"] == len(expected_to_fail)
    assert summary["passed"] == 0
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0

    assert failed_checks == set(expected_to_fail)

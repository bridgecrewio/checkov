from __future__ import annotations

from pathlib import Path

import pytest

from checkov.openapi.runner import Runner
from checkov.runner_filter import RunnerFilter
from tests.common.graph.checks.test_yaml_policies_base import load_yaml_data

BASE_DIR = Path(__file__).parent
CHECK_ID_MAP: "dict[str, str]" = {}  # will be filled via setup()


def test_GlobalSchemeDefineHTTP():
    run_check(base_path=BASE_DIR / "resource" / "v2", check="GlobalSchemeDefineHTTP")


def test_GlobalSecurityScopeUndefined():
    run_check(base_path=BASE_DIR / "resource" / "v2", check="GlobalSecurityScopeUndefined")


def test_Oauth2OperationObjectPasswordFlow():
    run_check(base_path=BASE_DIR / "resource" / "v2", check="Oauth2OperationObjectPasswordFlow")


def test_Oauth2SecurityDefinitionImplicitFlow():
    run_check(base_path=BASE_DIR / "resource" / "v2", check="Oauth2SecurityDefinitionImplicitFlow")


def test_Oauth2SecurityDefinitionPasswordFlow():
    run_check(base_path=BASE_DIR / "resource" / "v2", check="Oauth2SecurityDefinitionPasswordFlow")


def test_Oauth2SecurityPasswordFlow():
    run_check(base_path=BASE_DIR / "resource" / "v2", check="Oauth2SecurityPasswordFlow")


def test_Oauth2SecurityRequirement():
    run_check(base_path=BASE_DIR / "resource" / "v2", check="Oauth2SecurityRequirement")


def test_OperationObjectBasicAuth():
    run_check(base_path=BASE_DIR / "resource" / "v2", check="OperationObjectBasicAuth")


def test_OperationObjectConsumesUndefined():
    run_check(base_path=BASE_DIR / "resource" / "v2", check="OperationObjectConsumesUndefined")


def test_OperationObjectImplicitFlow():
    run_check(base_path=BASE_DIR / "resource" / "v2", check="OperationObjectImplicitFlow")


def test_OperationObjectProducesUndefined():
    run_check(base_path=BASE_DIR / "resource" / "v2", check="OperationObjectProducesUndefined")


def test_OperationObjectSecurityScopeUndefined():
    run_check(base_path=BASE_DIR / "resource" / "v2", check="OperationObjectSecurityScopeUndefined")


def test_PathSchemeDefineHTTP():
    run_check(base_path=BASE_DIR / "resource" / "v2", check="PathSchemeDefineHTTP")


def test_SecurityDefinitionBasicAuth():
    run_check(base_path=BASE_DIR / "resource" / "v2", check="SecurityDefinitionBasicAuth")


def test_SecurityDefinitions():
    run_check(base_path=BASE_DIR / "resource" / "v2", check="SecurityDefinitions")


def test_SecurityRequirement():
    run_check(base_path=BASE_DIR / "resource" / "v2", check="SecurityRequirement")


@pytest.fixture(autouse=True)
def setup():
    global CHECK_ID_MAP
    runner = Runner()
    registry = runner.import_registry()
    CHECK_ID_MAP = {check.__class__.__name__: check.id for entity, check in registry.all_checks()}


def run_check(base_path: Path, check: str) -> None:
    # set path where to find test files
    test_dir_path = base_path / f'example_{check}'

    # setup GitHub configuration runner
    runner = Runner()

    # run actual check
    report = runner.run(runner_filter=RunnerFilter(checks=CHECK_ID_MAP[check]), root_folder=str(test_dir_path))

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

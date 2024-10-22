from __future__ import annotations
from typing import Any

import pytest
from checkov.common.secrets.consts import ValidationStatus

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.models.enums import CheckResult

from checkov.common.output.secrets_record import SecretsRecord

from checkov.common.output.report import Report


@pytest.fixture
def secrets_report() -> Report:
    kwargs = {'check_id': 'mock', 'check_name': 'mock', 'code_block': 'mock', 'file_path': 'mock',
              'file_line_range': 'mock', 'evaluations': 'mock', 'check_class': 'mock', 'file_abs_path': 'mock'}
    record_1 = SecretsRecord(bc_check_id="VIOLATION_1", resource="RESOURCE_1",
                             check_result={"result": CheckResult.FAILED},
                             validation_status=ValidationStatus.VALID.value, **kwargs)
    record_2 = SecretsRecord(bc_check_id="VIOLATION_2", resource="RESOURCE_2",
                             check_result={"result": CheckResult.FAILED},
                             validation_status=ValidationStatus.INVALID.value, **kwargs)
    record_3 = SecretsRecord(bc_check_id="VIOLATION_3", resource="RESOURCE_3",
                             check_result={"result": CheckResult.FAILED},
                             validation_status=ValidationStatus.UNKNOWN.value, **kwargs)
    record_4 = SecretsRecord(bc_check_id="VIOLATION_4", resource="RESOURCE_4",
                             check_result={"result": CheckResult.FAILED},
                             validation_status=ValidationStatus.VALID.value, **kwargs)

    record_5 = SecretsRecord(bc_check_id="VIOLATION_1", resource="RESOURCE_1",
                             check_result={"result": CheckResult.PASSED},
                             validation_status=ValidationStatus.INVALID.value, **kwargs)

    report = Report(CheckType.SECRETS)
    report.add_record(record_1)
    report.add_record(record_2)
    report.add_record(record_3)
    report.add_record(record_4)
    report.add_record(record_5)

    return report


@pytest.fixture()
def json_reduced_check() -> dict[str, Any]:
    return {
        "check_id": "CKV_GHA_1",
        "check_name": "Ensure ACTIONS_ALLOW_UNSECURE_COMMANDS isn\u0027t true on environment variables",
        "check_result": {
            "result": "PASSED",
            "results_configuration": {}
        },
        "resource": "jobs(container-test-job)",
        "file_path": "/.github/workflows/image_no_violation.yml",
        "file_line_range": [
            7,
            7
        ],
        "file_abs_path": "/tmp/checkov/elturgeman6/elturgeman/supplygoat1/main/src/.github/workflows/image_no_violation.yml",
        "code_block": [
            [
                7,
                "    runs-on: ubuntu-latest\n"
            ],
        ],
        "bc_check_id": "BC_REPO_GITHUB_ACTION_1",
        "inspected_key_line": None,
        "evaluated_keys": None,
        "inspected_key": "",
        "inspected_value": ""
    }

@pytest.fixture()
def json_reduced_report() -> dict[str, Any]:
    return {
        "checks": {
            "passed_checks": [
                {
                    "check_id": "CKV_GHA_1",
                    "check_name": "Ensure ACTIONS_ALLOW_UNSECURE_COMMANDS isn\u0027t true on environment variables",
                    "check_result": {
                        "result": "PASSED",
                        "results_configuration": {}
                    },
                    "resource": "jobs(container-test-job)",
                    "file_path": "/.github/workflows/image_no_violation.yml",
                    "file_line_range": [
                        7,
                        7
                    ],
                    "file_abs_path": "/tmp/checkov/elturgeman6/elturgeman/supplygoat1/main/src/.github/workflows/image_no_violation.yml",
                    "code_block": [
                        [
                            7,
                            "    runs-on: ubuntu-latest\n"
                        ],
                    ],
                    "bc_check_id": "BC_REPO_GITHUB_ACTION_1",
                    "inspected_key_line": None,
                    "evaluated_keys": None,
                    "inspected_key": "",
                    "inspected_value": ""
                }
            ],
            "failed_checks": [
                {
                    "check_id": "CKV_GHA_2",
                    "check_name": "Ensure ACTIONS_ALLOW_UNSECURE_COMMANDS isn\u0027t true on environment variables",
                    "check_result": {
                        "result": "FAILED",
                        "results_configuration": {}
                    },
                    "resource": "jobs(container-test-job)",
                    "file_path": "/.github/workflows/image_no_violation.yml",
                    "file_line_range": [
                        7,
                        7
                    ],
                    "file_abs_path": "/tmp/checkov/elturgeman6/elturgeman/supplygoat1/main/src/.github/workflows/image_no_violation.yml",
                    "code_block": [
                        [
                            7,
                            "    runs-on: ubuntu-latest\n"
                        ],
                    ],
                    "bc_check_id": "BC_REPO_GITHUB_ACTION_1",
                    "inspected_key_line": None,
                    "evaluated_keys": None,
                    "inspected_key": "",
                    "inspected_value": ""
                }
            ],
            "skipped_checks": []
        },
        "image_cached_results": []
    }
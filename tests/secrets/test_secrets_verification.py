from __future__ import annotations
import os

import pytest
import responses

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.output.report import Report
from checkov.secrets.consts import VerifySecretsResult
from checkov.secrets.runner import Runner


def test_verify_secrets_insufficient_params_skip_download() -> None:
    os.environ["CKV_VALIDATE_SECRETS"] = "true"
    from checkov.common.bridgecrew.platform_integration import bc_integration
    bc_integration.skip_download = True
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"

    result = Runner().verify_secrets(Report(check_type=CheckType.SECRETS), "")

    os.environ.pop("CKV_VALIDATE_SECRETS", None)
    assert result == VerifySecretsResult.INSUFFICIENT_PARAMS


def test_verify_secrets_insufficient_params_no_api_key() -> None:
    os.environ["CKV_VALIDATE_SECRETS"] = "true"
    from checkov.common.bridgecrew.platform_integration import bc_integration
    bc_integration.bc_api_key = None

    result = Runner().verify_secrets(Report(check_type=CheckType.SECRETS), "")

    os.environ.pop("CKV_VALIDATE_SECRETS", None)
    assert result == VerifySecretsResult.INSUFFICIENT_PARAMS


def test_verify_secrets_insufficient_params_no_flag() -> None:
    # Not setting CKV_VALIDATE_SECRETS env var
    from checkov.common.bridgecrew.platform_integration import bc_integration
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"

    result = Runner().verify_secrets(Report(check_type=CheckType.SECRETS), "")

    assert result == VerifySecretsResult.INSUFFICIENT_PARAMS


@responses.activate
@pytest.mark.parametrize(
    "status_code",
    [
        (500,),
        (400,),
    ]
)
def test_verify_secrets_failure(mock_bc_integration, status_code: int) -> None:
    os.environ["CKV_VALIDATE_SECRETS"] = "True"
    os.environ["BC_API_KEY"] = "Key"

    responses.add(
        method=responses.POST,
        url=f"{mock_bc_integration.bc_api_url}/api/v1/secrets/reportVerification",
        json={},
        status=status_code
    )

    result = Runner().verify_secrets(Report(check_type=CheckType.SECRETS), "")

    assert result == VerifySecretsResult.FAILURE


@responses.activate
def test_verify_secrets(mock_bc_integration, secrets_report: Report) -> None:
    os.environ["CKV_VALIDATE_SECRETS"] = "True"
    os.environ["BC_API_KEY"] = "Key"
    violation_id_to_verify_status = {"VIOLATION_1": "Privileged",
                                     "VIOLATION_2": "Valid",
                                     "VIOLATION_3": "Invalid",
                                     "VIOLATION_4": "Unknown"}
    verified_report = [
            {
                "violationId": "VIOLATION_1",
                "resourceId": "mock:RESOURCE_1",
                "status": "Privileged"
            },
            {
                "violationId": "VIOLATION_2",
                "resourceId": "mock:RESOURCE_2",
                "status": "Valid"
            },
            {
                "violationId": "VIOLATION_3",
                "resourceId": "mock:RESOURCE_3",
                "status": "Invalid"
            },
            {
                "violationId": "VIOLATION_4",
                "resourceId": "mock:RESOURCE_4",
                "status": "Unknown"
            }
        ]

    responses.add(
        method=responses.POST,
        url=f"{mock_bc_integration.bc_api_url}/api/v1/secrets/reportVerification",
        json={'verificationReportSignedUrl': 'mock'},
        status=200
    )
    runner = Runner()
    runner.get_json_verification_report = lambda x: verified_report
    result = runner.verify_secrets(secrets_report, "path/to/enriched/secrets")

    assert result == VerifySecretsResult.SUCCESS
    for check in secrets_report.failed_checks:
        if hasattr(check, "validation_status"):
            assert check.validation_status == violation_id_to_verify_status[check.bc_check_id]
        else:
            raise Exception("Secrets record should have a validation status attribute")

    for check in secrets_report.passed_checks:
        if hasattr(check, "validation_status"):
            assert check.validation_status == 'mock'

from __future__ import annotations

import os
from unittest import mock

import pytest
import responses

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.secrets.consts import VerifySecretsResult


@mock.patch.dict(os.environ, {"CKV_VALIDATE_SECRETS": "true"})
def test_verify_secrets_insufficient_params_skip_download() -> None:
    from checkov.common.bridgecrew.platform_integration import bc_integration
    bc_integration.skip_download = True
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"

    from checkov.secrets.runner import Runner
    from checkov.common.output.report import Report
    result = Runner().verify_secrets(Report(check_type=CheckType.SECRETS), "")

    assert result == VerifySecretsResult.INSUFFICIENT_PARAMS


@mock.patch.dict(os.environ, {"CKV_VALIDATE_SECRETS": "true"})
def test_verify_secrets_insufficient_params_no_api_key() -> None:
    from checkov.common.bridgecrew.platform_integration import bc_integration
    bc_integration.bc_api_key = None

    from checkov.secrets.runner import Runner
    from checkov.common.output.report import Report
    result = Runner().verify_secrets(Report(check_type=CheckType.SECRETS), "")

    assert result == VerifySecretsResult.INSUFFICIENT_PARAMS


def test_verify_secrets_insufficient_params_no_flag() -> None:
    # Not setting CKV_VALIDATE_SECRETS env var
    from checkov.common.bridgecrew.platform_integration import bc_integration
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"

    from checkov.secrets.runner import Runner
    from checkov.common.output.report import Report
    result = Runner().verify_secrets(Report(check_type=CheckType.SECRETS), "")

    assert result == VerifySecretsResult.INSUFFICIENT_PARAMS

@mock.patch.dict(os.environ, {"CKV_VALIDATE_SECRETS": "true"})
def test_verify_secrets_insufficient_params_tenant_config_overrides_true_flag() -> None:
    from checkov.common.bridgecrew.platform_integration import bc_integration
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    bc_integration.customer_run_config_response = {'tenantConfig': {'secretsValidate': False}}

    from checkov.secrets.runner import Runner
    from checkov.common.output.report import Report
    result = Runner().verify_secrets(Report(check_type=CheckType.SECRETS), "")

    assert result == VerifySecretsResult.INSUFFICIENT_PARAMS


@mock.patch.dict(os.environ, {"CKV_VALIDATE_SECRETS": "false"})
def test_verify_secrets_insufficient_params_tenant_config_overrides_false_flag() -> None:
    from checkov.common.bridgecrew.platform_integration import bc_integration
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    bc_integration.customer_run_config_response = {'tenantConfig': {'secretsValidate': True}}
    bc_integration.skip_download = False

    from checkov.secrets.runner import Runner
    from checkov.common.output.report import Report
    result = Runner().verify_secrets(Report(check_type=CheckType.SECRETS), "")

    assert result != VerifySecretsResult.INSUFFICIENT_PARAMS

@mock.patch.dict(os.environ, {"CKV_VALIDATE_SECRETS": "false"})
def test_verify_secrets_insufficient_params_tenant_config_missing_false_flag() -> None:
    from checkov.common.bridgecrew.platform_integration import bc_integration
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    bc_integration.customer_run_config_response = {'tenantConfig': {'mock': True}}
    bc_integration.skip_download = False

    from checkov.secrets.runner import Runner
    from checkov.common.output.report import Report
    result = Runner().verify_secrets(Report(check_type=CheckType.SECRETS), "")

    assert result == VerifySecretsResult.INSUFFICIENT_PARAMS

@mock.patch.dict(os.environ, {"CKV_VALIDATE_SECRETS": "true"})
def test_verify_secrets_insufficient_params_tenant_config_missing_true_flag() -> None:
    from checkov.common.bridgecrew.platform_integration import bc_integration
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    bc_integration.customer_run_config_response = {'tenantConfig': {'mock': True}}
    bc_integration.skip_download = False

    from checkov.secrets.runner import Runner
    from checkov.common.output.report import Report
    result = Runner().verify_secrets(Report(check_type=CheckType.SECRETS), "")

    assert result != VerifySecretsResult.INSUFFICIENT_PARAMS

@responses.activate
@mock.patch.dict(os.environ, {"CKV_VALIDATE_SECRETS": "true"})
@pytest.mark.parametrize(
    "status_code",
    [
        (500,),
        (400,),
    ]
)
def test_verify_secrets_failure(mock_bc_integration, status_code: int) -> None:
    responses.add(
        method=responses.POST,
        url=f"{mock_bc_integration.api_url}/api/v1/secrets/reportVerification",
        json={},
        status=status_code
    )

    from checkov.secrets.runner import Runner
    from checkov.common.output.report import Report
    result = Runner().verify_secrets(Report(check_type=CheckType.SECRETS), "")

    assert result == VerifySecretsResult.FAILURE


@responses.activate
@mock.patch.dict(os.environ, {"CKV_VALIDATE_SECRETS": "true"})
def test_verify_secrets(mock_bc_integration, secrets_report) -> None:
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
        url=f"{mock_bc_integration.api_url}/api/v1/secrets/reportVerification",
        json={'verificationReportSignedUrl': 'mock'},
        status=200
    )

    from checkov.secrets.runner import Runner
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


@responses.activate
@mock.patch.dict(os.environ, {"CKV_VALIDATE_SECRETS": "true"})
def test_runner_verify_secrets(mock_bc_integration, mock_metadata_integration):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    valid_dir_path = current_dir + "/resources/cfn"

    rel_resource_path = '/secret.yml'
    resource_id = '25910f981e85ca04baf359199dd0bd4a3ae738b6'
    verified_report = [
        {
            "violationId": "BC_GIT_2",
            "resourceId": f"{rel_resource_path}:{resource_id}",
            "status": "Valid"
        }
    ]

    responses.add(
        method=responses.POST,
        url=f"{mock_bc_integration.api_url}/api/v1/secrets/reportVerification",
        json={'verificationReportSignedUrl': 'mock'},
        status=200
    )

    from checkov.secrets.runner import Runner
    runner = Runner()
    mock_bc_integration.persist_enriched_secrets = lambda x: 'mock'
    mock_bc_integration.bc_api_key = 'mock'
    runner.get_json_verification_report = lambda x: verified_report

    from checkov.runner_filter import RunnerFilter
    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets']))

    for check in report.failed_checks:
        if check.file_path == rel_resource_path and check.resource == resource_id:
            assert check.validation_status == 'Valid'
        else:
            assert check.validation_status == 'Unavailable'

import os
from unittest import mock

import responses
from checkov.common.models.enums import CheckResult


@responses.activate
@mock.patch.dict(os.environ, {"CKV_VALIDATE_SECRETS": "true"})
def test_runner_verify_secrets_skip_invalid_suppressed(mock_bc_integration, mock_metadata_integration):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    valid_dir_path = current_dir + "/resources/cfn"

    rel_resource_path = '/secret.yml'
    resource_id = '25910f981e85ca04baf359199dd0bd4a3ae738b6'
    verified_report = [
        {
            "violationId": "BC_GIT_2",
            "resourceId": f"{rel_resource_path}:{resource_id}",
            "status": "Invalid"
        }
    ]

    responses.add(
        method=responses.POST,
        url=f"{mock_bc_integration.api_url}/api/v1/secrets/reportVerification",
        json={'verificationReportSignedUrl': 'mock'},
        status=200
    )

    from checkov.runner_filter import RunnerFilter
    from checkov.secrets.runner import Runner
    runner = Runner()
    mock_bc_integration.persist_enriched_secrets = lambda x: 'mock'
    mock_bc_integration.bc_api_key = 'mock'
    runner.get_json_verification_report = lambda x: verified_report

    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], skip_checks=['Invalid']))

    assert len(report.skipped_checks) == 1
    assert report.skipped_checks[0].file_path == rel_resource_path
    assert report.skipped_checks[0].resource == resource_id
    assert report.skipped_checks[0].validation_status == 'Invalid'
    assert len(report.failed_checks) == 1
    assert report.failed_checks[0].validation_status != 'Invalid'


@responses.activate
@mock.patch.dict(os.environ, {"CKV_VALIDATE_SECRETS": "true"})
def test_runner_verify_secrets_skip_all_no_effect(mock_bc_integration, mock_metadata_integration):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    valid_dir_path = current_dir + "/resources/cfn"

    rel_resource_path = '/secret.yml'
    resource_id = '25910f981e85ca04baf359199dd0bd4a3ae738b6'
    second_resource_id = 'd70eab08607a4d05faa2d0d6647206599e9abc65'
    verified_report = [
        {
            "violationId": "BC_GIT_2",
            "resourceId": f"{rel_resource_path}:{resource_id}",
            "status": "Invalid"
        },
        {
            "violationId": "BC_GIT_6",
            "resourceId": f"{rel_resource_path}:{second_resource_id}",
            "status": "Unknown"
        }
    ]

    responses.add(
        method=responses.POST,
        url=f"{mock_bc_integration.api_url}/api/v1/secrets/reportVerification",
        json={'verificationReportSignedUrl': 'mock'},
        status=200
    )

    from checkov.runner_filter import RunnerFilter
    from checkov.secrets.runner import Runner
    runner = Runner()
    mock_bc_integration.persist_enriched_secrets = lambda x: 'mock'
    mock_bc_integration.bc_api_key = 'mock'

    runner.get_json_verification_report = lambda x: verified_report

    report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                        runner_filter=RunnerFilter(framework=['secrets'], skip_checks=['Invalid', 'Unknown', 'Valid']))

    assert len(report.skipped_checks) == 1
    assert report.skipped_checks[0].file_path == rel_resource_path
    assert report.skipped_checks[0].resource == resource_id
    assert report.skipped_checks[0].validation_status == 'Invalid'

    assert len(report.failed_checks) == 1
    assert report.failed_checks[0].file_path == rel_resource_path
    assert report.failed_checks[0].resource == second_resource_id
    assert report.failed_checks[0].validation_status == 'Unknown'


def test_modify_invalid_secrets_check_result_to_skipped(secrets_report_invalid_status) -> None:
    from checkov.secrets.runner import Runner
    Runner()._modify_invalid_secrets_check_result_to_skipped(secrets_report_invalid_status)

    assert len(secrets_report_invalid_status.failed_checks) == 0
    assert len(secrets_report_invalid_status.skipped_checks) == 4
    assert len(secrets_report_invalid_status.passed_checks) == 1

    assert all(check.check_result["result"] == CheckResult.SKIPPED
               for check in secrets_report_invalid_status.skipped_checks)
    assert all(check.check_result["suppress_comment"] == "Skipped invalid secret"
               for check in secrets_report_invalid_status.skipped_checks)



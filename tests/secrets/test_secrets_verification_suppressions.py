import os

import mock
import responses
from checkov.runner_filter import RunnerFilter

from checkov.secrets.runner import Runner


@responses.activate
@mock.patch.dict(os.environ, {"CKV_VALIDATE_SECRETS": "true"})
def test_runner_verify_secrets_skip_invalid_suppressed(mock_bc_integration, mock_metadata_integration):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    valid_dir_path = current_dir + "/resources/cfn"

    rel_resource_path = '/secret.yml'
    resource_id = '25910f981e85ca04baf359199dd0bd4a3ae738b6'
    verified_report = [
        {
            "violationId": "BC_GIT_6",
            "resourceId": f"{rel_resource_path}:{resource_id}",
            "status": "Invalid"
        }
    ]

    responses.add(
        method=responses.POST,
        url=f"{mock_bc_integration.bc_api_url}/api/v1/secrets/reportVerification",
        json={'verificationReportSignedUrl': 'mock'},
        status=200
    )

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

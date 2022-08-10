from pathlib import Path
from urllib.parse import quote_plus

import responses

from checkov.sca_image.runner import Runner
from checkov.github_actions.runner import Runner as GHA_Runner
from checkov.common.typing import _LicenseStatus

EXAMPLES_DIR = Path(__file__).parent / "examples/.github/workflows"


@responses.activate
def test_image_referencer_trigger_image_flow_calls(mock_bc_integration, image_name, cached_scan_result):
    # given
    image_id_encoded = quote_plus(f"image:{image_name}")

    responses.add(
        method=responses.GET,
        url=mock_bc_integration.bc_api_url + f"/api/v1/vulnerabilities/scan-results/{image_id_encoded}",
        json=cached_scan_result,
        status=200,
    )

    # when
    image_runner = Runner()
    image_runner.image_referencers = [GHA_Runner()]
    report = image_runner.run(root_folder=EXAMPLES_DIR)

    # then
    assert len(responses.calls) == 1
    responses.assert_call_count(
        mock_bc_integration.bc_api_url + f"/api/v1/vulnerabilities/scan-results/{image_id_encoded}", 1
    )

    assert len(report.failed_checks) == 3


@responses.activate
def test_licenses_status(mock_bc_integration):
    packages_input = [
        {"name": "docutils", "version": "0.15.2", "lang": "python"},
        {"name": "github.com/apparentlymart/go-textseg/v12", "version": "v12.0.0", "lang": "go"}
    ]

    response_json = {
        "violations": [
            {
                "name": "github.com/apparentlymart/go-textseg/v12",
                "version": "v12.0.0",
                "license": "NOT_FOUND",
                "policy": "BC_LIC_1",
                "status": "COMPLIANT"
            },
            {
                "name": "docutils",
                "version": "0.15.2",
                "license": "NOT_FOUND",
                "policy": "BC_LIC_1",
                "status": "COMPLIANT"
            },
        ]
    }

    # given
    responses.add(
        method=responses.POST,
        url=mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/packages/get-licenses-violations",
        json=response_json,
        status=200
    )

    image_runner = Runner()
    license_statuses = image_runner.get_license_statuses(packages_input)
    assert license_statuses == [
        _LicenseStatus(package_name='github.com/apparentlymart/go-textseg/v12', package_version='v12.0.0', policy='BC_LIC_1', license='', status='COMPLIANT'),
        _LicenseStatus(package_name='docutils', package_version='0.15.2', policy='BC_LIC_1', license='', status= 'COMPLIANT')
    ]

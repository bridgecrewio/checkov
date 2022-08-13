from pathlib import Path
from urllib.parse import quote_plus
import responses
import os
from unittest import mock

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.runner_filter import RunnerFilter
from checkov.sca_image.runner import Runner
from checkov.github_actions.runner import Runner as GHA_Runner
from checkov.common.typing import _LicenseStatus

EXAMPLES_DIR = Path(__file__).parent / "examples/.github/workflows"


@responses.activate
def test_image_referencer_trigger_image_flow_calls(mock_bc_integration, image_name, cached_scan_result):
    # given
    image_id_encoded = quote_plus(f"image:{image_name}")

    response_json = {
        "violations": [
            {
                "name": "readline",
                "version": "8.1.2-r0",
                "license": "Apache-2.0",
                "policy": "BC_LIC_1",
                "status": "OPEN"
            },
            {
                "name": "libnsl",
                "version": "2.0.0-r0",
                "license": "Apache-2.0",
                "policy": "BC_LIC_1",
                "status": "COMPLIANT"
            },
        ]
    }

    responses.add(
        method=responses.POST,
        url=mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/packages/get-licenses-violations",
        json=response_json,
        status=200
    )
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
    assert len(responses.calls) == 2
    responses.assert_call_count(
        mock_bc_integration.bc_api_url + f"/api/v1/vulnerabilities/scan-results/{image_id_encoded}", 1
    )
    responses.assert_call_count(
        mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/packages/get-licenses-violations", 1
    )

    assert len(report.failed_checks) == 4
    assert len(report.passed_checks) == 1


@responses.activate
def test_runner_honors_enforcement_rules(mock_bc_integration, image_name, cached_scan_result):
    # given
    image_id_encoded = quote_plus(f"image:{image_name}")

    response_json = {
        "violations": [
            {
                "name": "readline",
                "version": "8.1.2-r0",
                "license": "Apache-2.0",
                "policy": "BC_LIC_1",
                "status": "OPEN"
            },
            {
                "name": "libnsl",
                "version": "2.0.0-r0",
                "license": "Apache-2.0",
                "policy": "BC_LIC_1",
                "status": "COMPLIANT"
            },
        ]
    }

    responses.add(
        method=responses.POST,
        url=mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/packages/get-licenses-violations",
        json=response_json,
        status=200
    )
    responses.add(
        method=responses.GET,
        url=mock_bc_integration.bc_api_url + f"/api/v1/vulnerabilities/scan-results/{image_id_encoded}",
        json=cached_scan_result,
        status=200,
    )

    # when
    image_runner = Runner()
    filter = RunnerFilter(framework=['sca_image'], use_enforcement_rules=True)
    # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
    # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
    filter.enforcement_rule_configs = {CheckType.SCA_IMAGE: Severities[BcSeverities.OFF]}
    image_runner.image_referencers = [GHA_Runner()]
    report = image_runner.run(root_folder=EXAMPLES_DIR, runner_filter=filter)

    summary = report.get_summary()
    # then
    assert summary["passed"] == 0
    assert summary["failed"] == 0
    assert summary["skipped"] == 5
    assert summary["parsing_errors"] == 0


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
                "license": "Apache-2.0",
                "policy": "BC_LIC_1",
                "status": "COMPLIANT"
            },
            {
                "name": "docutils",
                "version": "0.15.2",
                "license": "Apache-2.0",
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
        _LicenseStatus(package_name='github.com/apparentlymart/go-textseg/v12', package_version='v12.0.0', policy='BC_LIC_1', license='Apache-2.0', status='COMPLIANT'),
        _LicenseStatus(package_name='docutils', package_version='0.15.2', policy='BC_LIC_1', license='Apache-2.0', status= 'COMPLIANT')
    ]


@mock.patch.dict(os.environ, {"REQUEST_MAX_TRIES": "1", "SLEEP_BETWEEN_REQUEST_TRIES": "0.01"})
@responses.activate
def test_licenses_status_on_failure(mock_bc_integration):
    packages_input = [
        {"name": "docutils", "version": "0.15.2", "lang": "python"},
        {"name": "github.com/apparentlymart/go-textseg/v12", "version": "v12.0.0", "lang": "go"}
    ]

    # given
    responses.add(
        method=responses.POST,
        url=mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/packages/get-licenses-violations",
        status=500
    )

    image_runner = Runner()
    try:
        # we expect to have failure here, in case the of http/connection error
        image_runner.get_license_statuses(packages_input)
        assert False
    except:
        assert True

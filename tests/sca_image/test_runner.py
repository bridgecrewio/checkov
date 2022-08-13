from __future__ import annotations

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
from checkov.common.models.enums import CheckResult
from .mocks import mock_scan, mock_scan_empty

WORKFLOW_EXAMPLES_DIR = Path(__file__).parent / "examples/.github/workflows"
DOCKERFILE_EXAMPLES_DIR = Path(__file__).parent / "examples/dockerfile"


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
    report = image_runner.run(root_folder=WORKFLOW_EXAMPLES_DIR)

    # then
    assert len(responses.calls) == 1
    responses.assert_call_count(
        mock_bc_integration.bc_api_url + f"/api/v1/vulnerabilities/scan-results/{image_id_encoded}", 1
    )

    assert len(report.failed_checks) == 3


@responses.activate
def test_runner_honors_enforcement_rules(mock_bc_integration, image_name, cached_scan_result):
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
    filter = RunnerFilter(framework=['sca_image'], use_enforcement_rules=True)
    # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
    # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
    filter.enforcement_rule_configs = {CheckType.SCA_IMAGE: Severities[BcSeverities.OFF]}
    image_runner.image_referencers = [GHA_Runner()]
    report = image_runner.run(root_folder=WORKFLOW_EXAMPLES_DIR, runner_filter=filter)

    summary = report.get_summary()
    # then
    assert summary["passed"] == 0
    assert summary["failed"] == 0
    assert summary["skipped"] == 3
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


@mock.patch('checkov.sca_image.runner.Runner.scan', mock_scan)
@responses.activate
def test_run(mock_bc_integration):
    # given
    response_json = {
        "violations": [
            {
                "name": "pcre2",
                "version": "10.39-3build1",
                "license": "Apache-2.0",
                "policy": "BC_LIC_1",
                "status": "COMPLIANT"
            },
            {
                "name": "perl",
                "version": "5.34.0-3ubuntu1",
                "license": "Apache-2.0-Fake",
                "policy": "BC_LIC_1",
                "status": "OPEN"
            },
        ]
    }
    responses.add(
        method=responses.POST,
        url=mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/packages/get-licenses-violations",
        json=response_json,
        status=200
    )

    runner = Runner()
    runner_filter = RunnerFilter(skip_checks=["CKV_CVE_2022_1586"])
    # when
    dockerfile_path = "/path/to/Dockerfile"
    image_id = "sha256:123456"
    report = runner.run(root_folder=DOCKERFILE_EXAMPLES_DIR, runner_filter=runner_filter, dockerfile_path=dockerfile_path, image_id=image_id)

    # then
    rootless_path = "path/to/Dockerfile"
    assert report.check_type == "sca_image"
    assert report.resources == {f'{rootless_path} (sha256:123456).pcre2', f'{rootless_path} (sha256:123456).perl'}

    assert len(report.passed_checks) == 1
    assert len(report.failed_checks) == 3
    assert len(report.skipped_checks) == 1
    assert len(report.parsing_errors) == 0

    cve_record = next((c for c in report.failed_checks if c.resource == f"{rootless_path} (sha256:123456).pcre2" and c.check_name == "SCA package scan"), None)
    assert cve_record is not None
    assert cve_record.bc_check_id == "BC_CVE_2022_1587"
    assert cve_record.check_id == "CKV_CVE_2022_1587"
    assert cve_record.check_class == "checkov.common.bridgecrew.vulnerability_scanning.image_scanner.ImageScanner"  # not the real one
    assert cve_record.check_name == "SCA package scan"
    assert cve_record.check_result == {"result": CheckResult.FAILED}
    assert cve_record.code_block == [(0, "pcre2: 10.39-3build1")]
    assert cve_record.description == (
        "An out-of-bounds read vulnerability was discovered in the PCRE2 library in the get_recurse_data_length() function of the pcre2_jit_compile.c file. "
        "This issue affects recursions in JIT-compiled regular expressions caused by duplicate data transfers."
    )
    assert cve_record.file_abs_path == f"/{rootless_path}"
    assert cve_record.file_line_range == [0, 0]
    assert cve_record.file_path == f"/{rootless_path} (sha256:123456)"
    assert cve_record.repo_file_path == f"/{rootless_path}"
    assert cve_record.resource == f"{rootless_path} (sha256:123456).pcre2"
    assert cve_record.severity == Severities[BcSeverities.LOW]
    assert cve_record.short_description == "CVE-2022-1587 - pcre2: 10.39-3build1"
    assert cve_record.vulnerability_details["lowest_fixed_version"] == "N/A"
    assert cve_record.vulnerability_details["fixed_versions"] == []

    assert {"licenses", "package_type"} <= cve_record.vulnerability_details.keys()
    assert cve_record.vulnerability_details["licenses"] == "Apache-2.0"
    assert cve_record.vulnerability_details["package_type"] == "os"

    skipped_record = report.skipped_checks[0]
    assert skipped_record.check_result == {"result": CheckResult.SKIPPED, 'suppress_comment': 'CVE-2022-1586 is skipped'}
    assert skipped_record.short_description == "CVE-2022-1586 - pcre2: 10.39-3build1"

    # making sure extra-resources (a scanned packages without cves) also have licenses - this data will be printed
    # as part of the BON report.
    extra_resource = next((c for c in report.extra_resources if c.resource == f"{rootless_path} (sha256:123456).bzip2"), None)
    assert extra_resource is not None
    assert "licenses" in extra_resource.vulnerability_details
    assert extra_resource.vulnerability_details["licenses"] == "Unknown"

    license_resource = next((c for c in report.failed_checks if c.check_name == "SCA license" if
                             c.resource == f"{rootless_path} (sha256:123456).perl"), None)
    assert license_resource is not None
    print(license_resource.resource)
    assert license_resource.check_id == "BC_LIC_1"
    assert license_resource.bc_check_id == "BC_LIC_1"
    assert license_resource.check_result == {"result": CheckResult.FAILED}

    assert {"package_name", "package_name", "license", "status",
            "policy", "package_type"} <= license_resource.vulnerability_details.keys()
    assert license_resource.vulnerability_details["package_name"] == "perl"
    assert license_resource.vulnerability_details["package_version"] == "5.34.0-3ubuntu1"
    assert license_resource.vulnerability_details["license"] == "Apache-2.0-Fake"
    assert license_resource.vulnerability_details["status"] == "FAILED"
    assert license_resource.vulnerability_details["policy"] == "BC_LIC_1"
    assert license_resource.vulnerability_details["package_type"] == "os"


@mock.patch('checkov.sca_image.runner.Runner.scan', mock_scan_empty)
@responses.activate
def test_run_with_empty_scan_result(mock_bc_integration):
    # given
    response_json = {
        "violations": [
            {
                "name": "pcre2",
                "version": "10.39-3build1",
                "license": "Apache-2.0",
                "policy": "BC_LIC_1",
                "status": "COMPLIANT"
            },
            {
                "name": "perl",
                "version": "5.34.0-3ubuntu1",
                "license": "Apache-2.0-Fake",
                "policy": "BC_LIC_1",
                "status": "OPEN"
            },
        ]
    }
    responses.add(
        method=responses.POST,
        url=mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/packages/get-licenses-violations",
        json=response_json,
        status=200
    )

    runner = Runner()
    runner_filter = RunnerFilter(skip_checks=["CKV_CVE_2022_1586"])
    # when
    dockerfile_path = "/Users/ipeleg/Work/checkov/tests/sca_image/examples/dockerfile/Dockerfile"
    image_id = "sha256:123456"
    report = runner.run(root_folder=DOCKERFILE_EXAMPLES_DIR, runner_filter=runner_filter, dockerfile_path=dockerfile_path, image_id=image_id)

    # then
    assert report.check_type == "sca_image"
    assert report.resources == set()

    assert len(report.passed_checks) == 0
    assert len(report.failed_checks) == 0
    assert len(report.skipped_checks) == 0
    assert len(report.parsing_errors) == 0

from __future__ import annotations

import os
from pathlib import Path
from unittest import mock
from urllib.parse import quote_plus

import responses
from aioresponses import aioresponses
from yarl import URL

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.code_categories import CodeCategoryType
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.common.models.enums import CheckResult
from checkov.github_actions.runner import Runner as GHA_Runner
from checkov.runner_filter import RunnerFilter
from checkov.sca_image.runner import Runner
from .mocks import mock_scan_empty, mock_scan_image

WORKFLOW_EXAMPLES_DIR = Path(__file__).parent / "examples/.github/workflows"
WORKFLOW_IMAGE_EXAMPLES_DIR = Path(__file__).parent / "examples/example/.github/workflows"
DOCKERFILE_EXAMPLES_DIR = Path(__file__).parent / "examples/dockerfile"


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
    with aioresponses() as mock_response:
        mock_response.post(
            url=mock_bc_integration.api_url + "/api/v1/vulnerabilities/packages/get-licenses-violations",
            payload=response_json,
            status=200
        )
        mock_response.get(
            url=URL(mock_bc_integration.api_url + f"/api/v1/vulnerabilities/scan-results/{image_id_encoded}",
                    encoded=True),
            payload=cached_scan_result,
            status=200,
        )

        # when
        reports = GHA_Runner().run(root_folder=str(WORKFLOW_EXAMPLES_DIR),
                                   runner_filter=RunnerFilter(run_image_referencer=True))

        sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    # then
    assert len(sca_image_report.failed_checks) == 4
    assert len(sca_image_report.passed_checks) == 1


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

    with aioresponses() as mock_response:
        mock_response.post(
            url=mock_bc_integration.api_url + "/api/v1/vulnerabilities/packages/get-licenses-violations",
            payload=response_json,
            status=200
        )
        mock_response.get(
            url=URL(mock_bc_integration.api_url + f"/api/v1/vulnerabilities/scan-results/{image_id_encoded}", encoded=True),
            payload=cached_scan_result,
            status=200,
        )

        # when
        runner_filter = RunnerFilter(use_enforcement_rules=True, run_image_referencer=True)
        # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
        # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
        runner_filter.enforcement_rule_configs = {
            CheckType.GITHUB_ACTIONS: Severities[BcSeverities.OFF],
            CheckType.SCA_IMAGE: {
                CodeCategoryType.LICENSES: Severities[BcSeverities.OFF],
                CodeCategoryType.VULNERABILITIES: Severities[BcSeverities.OFF]
            }
        }

        reports = GHA_Runner().run(root_folder=str(WORKFLOW_EXAMPLES_DIR), runner_filter=runner_filter)
        sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

        summary = sca_image_report.get_summary()
    # then
    assert summary["passed"] == 0
    assert summary["failed"] == 0
    assert summary["skipped"] == 5
    assert summary["parsing_errors"] == 0


def test_run(sca_image_report):
    # given
    report = sca_image_report

    # then
    rootless_path = "path/to/Dockerfile"
    assert report.check_type == "sca_image"
    assert report.resources == {f'{rootless_path} (sha256:123456).pcre2', f'{rootless_path} (sha256:123456).perl'}

    assert len(report.passed_checks) == 1
    assert len(report.failed_checks) == 3
    assert len(report.skipped_checks) == 1
    assert len(report.parsing_errors) == 0

    cve_record = next((c for c in report.failed_checks if
                       c.resource == f"{rootless_path} (sha256:123456).pcre2" and c.check_name == "SCA package scan"),
                      None)
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
    assert skipped_record.check_result == {"result": CheckResult.SKIPPED,
                                           'suppress_comment': 'CVE-2022-1586 is skipped'}
    assert skipped_record.short_description == "CVE-2022-1586 - pcre2: 10.39-3build1"

    # making sure extra-resources (a scanned packages without cves) also have licenses - this data will be printed
    # as part of the BON report.
    extra_resource = next((c for c in report.extra_resources if c.resource == f"{rootless_path} (sha256:123456).bzip2"),
                          None)
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


def test_run_license_policy(mock_bc_integration, image_name, cached_scan_result):
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
    with aioresponses() as mock_response:
        mock_response.post(
            url=mock_bc_integration.api_url + "/api/v1/vulnerabilities/packages/get-licenses-violations",
            payload=response_json,
            status=200
        )
        mock_response.get(
            url=URL(mock_bc_integration.api_url + f"/api/v1/vulnerabilities/scan-results/{image_id_encoded}", encoded=True),
            payload=cached_scan_result,
            status=200,
        )

        # when
        runner_filter = RunnerFilter(checks=['BC_LIC_1'], run_image_referencer=True)
        reports = GHA_Runner().run(root_folder=str(WORKFLOW_EXAMPLES_DIR), runner_filter=runner_filter)
        sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)
    # then
    assert not [c for c in sca_image_report.passed_checks + sca_image_report.failed_checks
                if c.check_id.startswith('CKV_CVE')]


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
        url=mock_bc_integration.api_url + "/api/v1/vulnerabilities/packages/get-licenses-violations",
        json=response_json,
        status=200
    )

    runner = Runner()
    runner_filter = RunnerFilter(skip_checks=["CKV_CVE_2022_1586"])
    # when
    dockerfile_path = "/Users/ipeleg/Work/checkov/tests/sca_image/examples/dockerfile/Dockerfile"
    image_id = "sha256:123456"
    report = runner.run(root_folder=DOCKERFILE_EXAMPLES_DIR, runner_filter=runner_filter,
                        dockerfile_path=dockerfile_path, image_id=image_id)

    # then
    assert report.check_type == "sca_image"
    assert report.resources == set()

    assert len(report.passed_checks) == 0
    assert len(report.failed_checks) == 0
    assert len(report.skipped_checks) == 0
    assert len(report.parsing_errors) == 0


@mock.patch.dict(os.environ, {"CKV_IGNORE_HIDDEN_DIRECTORIES": "false"})
@mock.patch('checkov.sca_image.runner.Runner.get_image_cached_results', mock_scan_image)
def test_run_with_image_cached_reports_env(mock_bc_integration, image_name2, cached_scan_result2):
    image_id_encoded = quote_plus(f"image:{image_name2}")

    with aioresponses() as mock_response:
        mock_response.get(
            url=URL(mock_bc_integration.api_url + f"/api/v1/vulnerabilities/scan-results/{image_id_encoded}", encoded=True),
            payload=cached_scan_result2,
            status=200,
        )

        runner_filter = RunnerFilter(run_image_referencer=True)
        reports = GHA_Runner().run(root_folder=str(WORKFLOW_IMAGE_EXAMPLES_DIR), runner_filter=runner_filter)
        sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(sca_image_report.passed_checks) == 0
    assert len(sca_image_report.failed_checks) == 1
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0
    assert len(sca_image_report.image_cached_results) == 1


@mock.patch.dict(os.environ, {"CHECKOV_CREATE_SCA_IMAGE_REPORTS_FOR_IR": "False"})
@mock.patch.dict(os.environ, {"CKV_IGNORE_HIDDEN_DIRECTORIES": "false"})
@mock.patch('checkov.sca_image.runner.Runner.get_image_cached_results', mock_scan_image)
def test_run_with_image_cached_reports_and_without_sca_reports_env(mock_bc_integration, image_name2,
                                                                   cached_scan_result2):
    image_id_encoded = quote_plus(f"image:{image_name2}")
    with aioresponses() as mock_response:
        mock_response.get(
            url=URL(mock_bc_integration.api_url + f"/api/v1/vulnerabilities/scan-results/{image_id_encoded}", encoded=True),
            payload=cached_scan_result2,
            status=200,
        )

        runner_filter = RunnerFilter(run_image_referencer=True)
        reports = GHA_Runner().run(root_folder=str(WORKFLOW_IMAGE_EXAMPLES_DIR), runner_filter=runner_filter)
        sca_image_report = next(report for report in reports if report.check_type == CheckType.SCA_IMAGE)

    assert len(sca_image_report.passed_checks) == 0
    assert len(sca_image_report.failed_checks) == 1
    assert len(sca_image_report.skipped_checks) == 0
    assert len(sca_image_report.parsing_errors) == 0
    assert len(sca_image_report.image_cached_results) == 1


@responses.activate
def test_run_with_error_from_scan_results(mock_bc_integration, image_name2, cached_scan_result3):
    image_id_encoded = quote_plus(f"image:{image_name2}")

    responses.add(
        method=responses.GET,
        url=mock_bc_integration.api_url + f"/api/v1/vulnerabilities/scan-results/{image_id_encoded}",
        json=cached_scan_result3,
        status=500,
    )

    runner = Runner()
    runner_filter = RunnerFilter(skip_checks=["CKV_CVE_2022_1586"])
    # when
    image_id = "sha256:123456"
    report = runner.run(root_folder=DOCKERFILE_EXAMPLES_DIR, runner_filter=runner_filter, image_id=image_id,
                        files=[".github/workflows/vulnerable_container.yaml"])

    assert len(report.passed_checks) == 0
    assert len(report.failed_checks) == 0
    assert len(report.skipped_checks) == 0
    assert len(report.parsing_errors) == 0
    assert len(report.image_cached_results) == 0

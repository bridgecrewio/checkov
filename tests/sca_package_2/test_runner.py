import os
from pathlib import Path
from unittest.mock import MagicMock

from pytest_mock import MockerFixture
from packaging import version as packaging_version

from checkov.common.bridgecrew.bc_source import SourceTypes, BCSourceType
from checkov.common.bridgecrew.code_categories import CodeCategoryType
from checkov.common.bridgecrew.platform_integration import bc_integration, FileToPersist
from checkov.runner_filter import RunnerFilter
from checkov.sca_package_2.runner import Runner
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.common.models.enums import CheckResult, ErrorStatus

EXAMPLES_DIR = Path(__file__).parent / "examples"


def test_upload_scannable_files():
    # when
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    input_paths = Runner().upload_package_files(
        root_path=EXAMPLES_DIR,
        files=[],
        excluded_paths=set(),
    )

    # expected
    expected_output = {
        FileToPersist(full_file_path=str(EXAMPLES_DIR / 'requirements.txt'),
                      s3_file_key='requirements.txt'),
        FileToPersist(full_file_path=str(EXAMPLES_DIR / 'go.sum'),
                      s3_file_key='go.sum'),
        FileToPersist(full_file_path=str(EXAMPLES_DIR / 'package-lock.json'),
                      s3_file_key='package-lock.json'),
        FileToPersist(full_file_path=str(EXAMPLES_DIR / 'package.json'),
                      s3_file_key='package.json'),
        FileToPersist(full_file_path=str(EXAMPLES_DIR / 'go.mod'),
                      s3_file_key='go.mod'),
        FileToPersist(full_file_path=str(EXAMPLES_DIR / 'Microsoft.NET.Sdk.csproj'),
                      s3_file_key='Microsoft.NET.Sdk.csproj')
    }

    # then
    assert len(input_paths) == 6

    assert set(input_paths) == expected_output


def test_upload_scannable_files_exclude_go_and_requirements():
    # when
    input_output_paths = Runner().upload_package_files(
        root_path=EXAMPLES_DIR,
        files=[],
        excluded_paths=set(),
        excluded_file_names={"go.sum", "package-lock.json"}
    )
    # expected
    expected_output = {
        FileToPersist(full_file_path=str(EXAMPLES_DIR / 'requirements.txt'),
                      s3_file_key='requirements.txt'),
        FileToPersist(full_file_path=str(EXAMPLES_DIR / 'package.json'),
                      s3_file_key='package.json'),
        FileToPersist(full_file_path=str(EXAMPLES_DIR / 'go.mod'),
                      s3_file_key='go.mod'),
        FileToPersist(full_file_path=str(EXAMPLES_DIR / 'Microsoft.NET.Sdk.csproj'),
                      s3_file_key='Microsoft.NET.Sdk.csproj')
    }

    # then
    assert len(input_output_paths) == 4

    assert set(input_output_paths) == expected_output


def test_upload_scannable_files_file_config():
    origin_cwd = os.getcwd()
    try:
        # setup
        os.chdir(str(Path(__file__).parent))

        # when
        input_output_paths = Runner().upload_package_files(
            root_path=None,
            files=[
                str(EXAMPLES_DIR / 'requirements.txt'),
                str(EXAMPLES_DIR / 'go.sum'),
                str(EXAMPLES_DIR / 'package-lock.json'),
                str(EXAMPLES_DIR / 'package.json'),
                str(EXAMPLES_DIR / 'go.mod'),
                str(EXAMPLES_DIR / 'Microsoft.NET.Sdk.csproj')
            ],
            excluded_paths=set(),
            excluded_file_names=set()
        )
        # expected (paths are in related to the test-working-dir)
        expected_output = {
            FileToPersist(full_file_path=str(EXAMPLES_DIR / 'requirements.txt'),
                          s3_file_key='examples/requirements.txt'),
            FileToPersist(full_file_path=str(EXAMPLES_DIR / 'go.sum'),
                          s3_file_key='examples/go.sum'),
            FileToPersist(full_file_path=str(EXAMPLES_DIR / 'package-lock.json'),
                          s3_file_key='examples/package-lock.json'),
            FileToPersist(full_file_path=str(EXAMPLES_DIR / 'package.json'),
                          s3_file_key='examples/package.json'),
            FileToPersist(full_file_path=str(EXAMPLES_DIR / 'go.mod'),
                          s3_file_key='examples/go.mod'),
            FileToPersist(full_file_path=str(EXAMPLES_DIR / 'Microsoft.NET.Sdk.csproj'),
                          s3_file_key='examples/Microsoft.NET.Sdk.csproj')
        }

        # then
        assert len(input_output_paths) == 6

        assert set(input_output_paths) == expected_output
    finally:
        # teardown
        os.chdir(origin_cwd)


def test_run(sca_package_2_report):
    # given
    report = sca_package_2_report
    # then
    assert report.check_type == "sca_package"

    assert report.resources == {
        "path/to/go.sum.github.com/dgrijalva/jwt-go",
        "path/to/go.sum.golang.org/x/crypto",
        "requirements.txt.django",
        "requirements.txt.flask",
        "requirements.txt.requests",
        "path/to/sub/requirements.txt.requests",
    }

    assert len(report.passed_checks) == 3
    assert len(report.failed_checks) == 7
    assert len(report.skipped_checks) == 3
    assert len(report.parsing_errors) == 0

    cve_record = next((c for c in report.failed_checks if
                       c.resource == "path/to/go.sum.golang.org/x/crypto" and c.check_name == "SCA package scan"), None)
    assert cve_record is not None
    assert cve_record.bc_check_id == "BC_CVE_2020_29652"
    assert cve_record.check_id == "CKV_CVE_2020_29652"
    assert cve_record.check_class == "unittest.mock.MagicMock"  # not the real one
    assert cve_record.check_name == "SCA package scan"
    assert cve_record.check_result == {"result": CheckResult.FAILED}
    assert cve_record.code_block == [(0, "golang.org/x/crypto: v0.0.1")]
    assert cve_record.description == (
        "A nil pointer dereference in the golang.org/x/crypto/ssh component through v0.0.3 "
        "for Go allows remote attackers to cause a denial of service against SSH servers."
    )
    assert cve_record.file_abs_path == "/path/to/go.sum"
    assert cve_record.file_line_range == [0, 0]
    assert cve_record.file_path == "/path/to/go.sum"
    assert cve_record.repo_file_path == "/path/to/go.sum"
    assert cve_record.resource == "path/to/go.sum.golang.org/x/crypto"
    assert cve_record.severity == Severities[BcSeverities.HIGH]
    assert cve_record.short_description == "CVE-2020-29652 - golang.org/x/crypto: v0.0.1"
    assert cve_record.vulnerability_details["lowest_fixed_version"] == "0.0.2"
    assert cve_record.vulnerability_details["fixed_versions"] == [
        packaging_version.parse("v0.0.2"),
    ]

    # making sure cve-records have licenses (the one belongs to the associated package) - this data will be printed
    # as part of the BON report.
    cve_record_with_license = next((c for c in report.failed_checks if
                                    c.resource == "requirements.txt.django" and c.check_name == "SCA package scan"),
                                   None)
    assert cve_record_with_license is not None
    assert "licenses" in cve_record_with_license.vulnerability_details
    assert cve_record_with_license.vulnerability_details["licenses"] == "OSI_BDS"

    cve_record_with_2_license = next((c for c in report.failed_checks if
                                      c.resource == "requirements.txt.flask" and c.check_name == "SCA package scan"),
                                     None)
    assert cve_record_with_2_license is not None
    assert "licenses" in cve_record_with_2_license.vulnerability_details
    assert cve_record_with_2_license.vulnerability_details["licenses"] == '"OSI_APACHE","DUMMY_OTHER_LICENSE"'

    # making sure extra-resources (a scanned packages without cves) also have licenses - this data will be printed
    # as part of the BON report.
    extra_resource = next((c for c in report.extra_resources if c.resource == "requirements.txt.requests"),
                          None)
    assert extra_resource is not None
    assert "licenses" in extra_resource.vulnerability_details
    assert extra_resource.vulnerability_details["licenses"] == "OSI_APACHE"

    license_resource = next((c for c in report.failed_checks if c.check_name == "SCA license" if
                             c.resource == "requirements.txt.flask"), None)
    assert license_resource is not None
    assert license_resource.check_id == "BC_LIC_1"
    assert license_resource.bc_check_id == "BC_LIC_1"
    assert license_resource.check_result == {"result": CheckResult.FAILED}
    assert {"package_name", "package_name", "license", "status",
            "policy"} <= license_resource.vulnerability_details.keys()
    assert license_resource.vulnerability_details["package_name"] == "flask"
    assert license_resource.vulnerability_details["package_version"] == "0.6"
    assert license_resource.vulnerability_details["license"] == "DUMMY_OTHER_LICENSE"
    assert license_resource.vulnerability_details["status"] == "FAILED"
    assert license_resource.vulnerability_details["policy"] == "BC_LIC_1"


def test_runner_honors_enforcement_rules(mocker: MockerFixture, scan_result_2):
    # given
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    scanner_mock = MagicMock()
    scanner_mock.return_value.scan.return_value = scan_result_2
    mocker.patch("checkov.sca_package_2.runner.Scanner", side_effect=scanner_mock)

    # when
    runner = Runner()
    filter = RunnerFilter(framework=['sca_package'], use_enforcement_rules=True)
    # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
    # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
    filter.enforcement_rule_configs = {
        CheckType.SCA_PACKAGE: {
            CodeCategoryType.LICENSES: Severities[BcSeverities.OFF],
            CodeCategoryType.VULNERABILITIES: Severities[BcSeverities.OFF]
        }
    }
    report = runner.run(root_folder=EXAMPLES_DIR, runner_filter=filter)

    # then
    summary = report.get_summary()
    # then
    assert summary["passed"] == 0
    assert summary["failed"] == 0
    assert summary["skipped"] > 0

    assert any(c for c in report.skipped_checks if c.check_id.startswith('CKV_CVE'))
    assert any(c for c in report.skipped_checks if c.check_id.startswith('BC_LIC'))

    assert summary["parsing_errors"] == 0


def test_run_license_policy(mocker: MockerFixture, scan_result_2):
    # given
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    scanner_mock = MagicMock()
    scanner_mock.return_value.scan.return_value = scan_result_2
    mocker.patch("checkov.sca_package_2.runner.Scanner", side_effect=scanner_mock)

    # when
    runner = Runner()
    filter = RunnerFilter(framework=['sca_package'], checks=['BC_LIC_1'])
    report = runner.run(root_folder=EXAMPLES_DIR, runner_filter=filter)

    # then
    assert not [c for c in report.passed_checks + report.failed_checks if c.check_id.startswith('CKV_CVE')]


def test_run_with_empty_scan_result(mocker: MockerFixture):
    # given
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    scanner_mock = MagicMock()
    scanner_mock.return_value.scan.return_value = dict()
    mocker.patch("checkov.sca_package_2.runner.Scanner", side_effect=scanner_mock)

    # when
    report = Runner().run(root_folder=EXAMPLES_DIR)

    # then
    assert report.check_type == "sca_package"
    assert report.resources == set()


def test_run_with_ide_source_and_bc_api_key(mocker: MockerFixture):
    # given
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    bc_integration.bc_source = SourceTypes[BCSourceType.JETBRAINS]

    scanner_mock = MagicMock()
    mocker.patch("checkov.sca_package_2.runner.Scanner", side_effect=scanner_mock)

    # when
    report = Runner().run(root_folder=EXAMPLES_DIR)

    #
    bc_integration.bc_source = None

    # then
    assert report.check_type == "sca_package"
    assert report.resources == set()
    assert report.error_status == ErrorStatus.SUCCESS  # shouldn't be ERROR

    # scanner shouldn't be invoked
    scanner_mock.assert_not_called()
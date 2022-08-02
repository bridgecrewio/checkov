from pathlib import Path

from mock.mock import MagicMock
from packaging import version as packaging_version
from pytest_mock import MockerFixture

from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.common.models.enums import CheckResult
from checkov.runner_filter import RunnerFilter
from checkov.sca_package.runner import Runner

EXAMPLES_DIR = Path(__file__).parent / "examples"


def test_run(mocker: MockerFixture, scan_result):
    # given
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    scanner_mock = MagicMock()
    scanner_mock.return_value.scan.return_value = scan_result
    mocker.patch("checkov.sca_package.runner.Scanner", side_effect=scanner_mock)

    # when
    report = Runner().run(root_folder=EXAMPLES_DIR)

    # then
    assert report.check_type == "sca_package"
    assert report.resources == {
        "path/to/go.sum.github.com/dgrijalva/jwt-go",
        "path/to/go.sum.golang.org/x/crypto",
        "path/to/requirements.txt.django",
        "path/to/requirements.txt.flask",
    }
    assert len(report.passed_checks) == 0
    assert len(report.failed_checks) == 12
    assert len(report.skipped_checks) == 0
    assert len(report.parsing_errors) == 0

    cve_record = next((c for c in report.failed_checks if c.resource == "path/to/go.sum.golang.org/x/crypto" and c.check_name == "SCA package scan"), None)
    assert cve_record is not None
    assert cve_record.bc_check_id == "BC_CVE_2020_29652"
    assert cve_record.check_id == "CKV_CVE_2020_29652"
    assert cve_record.check_class == "mock.mock.MagicMock"  # not the real one
    assert cve_record.check_name == "SCA package scan"
    assert cve_record.check_result == {"result": CheckResult.FAILED}
    assert cve_record.code_block == [(0, "golang.org/x/crypto: v0.0.0-20200622213623-75b288015ac9")]
    assert cve_record.description == (
        "A nil pointer dereference in the golang.org/x/crypto/ssh component through v0.0.0-20201203163018-be400aefbc4c "
        "for Go allows remote attackers to cause a denial of service against SSH servers."
    )
    assert cve_record.file_abs_path == "/path/to/go.sum"
    assert cve_record.file_line_range == [0, 0]
    assert cve_record.file_path == "/path/to/go.sum"
    assert cve_record.repo_file_path == "/path/to/go.sum"
    assert cve_record.resource == "path/to/go.sum.golang.org/x/crypto"
    assert cve_record.severity == Severities[BcSeverities.HIGH]
    assert cve_record.short_description == "CVE-2020-29652 - golang.org/x/crypto: v0.0.0-20200622213623-75b288015ac9"
    assert cve_record.vulnerability_details["lowest_fixed_version"] == "v0.0.0-20201216223049-8b5274cf687f"
    assert cve_record.vulnerability_details["fixed_versions"] == [
        packaging_version.parse("v0.0.0-20201216223049-8b5274cf687f"),
    ]

    cve_record_with_license = next((c for c in report.failed_checks if c.resource == "path/to/requirements.txt.django" and c.check_name == "SCA package scan"), None)
    assert cve_record_with_license is not None
    assert "licenses" in cve_record_with_license.vulnerability_details
    assert cve_record_with_license.vulnerability_details["licenses"] == "OSI_BDS"

    cve_record_with_2_license = next((c for c in report.failed_checks if c.resource == "path/to/requirements.txt.flask" and c.check_name == "SCA package scan"), None)
    assert cve_record_with_2_license is not None
    assert "licenses" in cve_record_with_2_license.vulnerability_details
    assert cve_record_with_2_license.vulnerability_details["licenses"] == "OSI_APACHE, DUMMY_OTHER_LICENSE"


def test_run_with_empty_scan_result(mocker: MockerFixture):
    # given
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    scanner_mock = MagicMock()
    scanner_mock.return_value.scan.return_value = []
    mocker.patch("checkov.sca_package.runner.Scanner", side_effect=scanner_mock)

    # when
    report = Runner().run(root_folder=EXAMPLES_DIR)

    # then
    assert report.check_type == "sca_package"
    assert report.resources == set()


def test_run_with_skip(mocker: MockerFixture, scan_result):
    # given
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    scanner_mock = MagicMock()
    scanner_mock.return_value.scan.return_value = scan_result
    mocker.patch("checkov.sca_package.runner.Scanner", side_effect=scanner_mock)
    runner_filter = RunnerFilter(skip_checks=["CKV_CVE_2020_29652"])

    # when
    report = Runner().run(root_folder=EXAMPLES_DIR, runner_filter=runner_filter)

    # then
    assert report.check_type == "sca_package"
    assert report.resources == {
        "path/to/go.sum.github.com/dgrijalva/jwt-go",
        "path/to/go.sum.golang.org/x/crypto",
        "path/to/requirements.txt.django",
        "path/to/requirements.txt.flask",
    }
    assert len(report.passed_checks) == 0
    assert len(report.failed_checks) == 11
    assert len(report.skipped_checks) == 1
    assert len(report.parsing_errors) == 0

    record = report.skipped_checks[0]
    assert record.check_id == "CKV_CVE_2020_29652"


def test_prepare_and_scan(mocker: MockerFixture, scan_result):
    # given
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    scanner_mock = MagicMock()
    scanner_mock.return_value.scan.return_value = scan_result
    mocker.patch("checkov.sca_package.runner.Scanner", side_effect=scanner_mock)

    # when
    runner = Runner()
    real_result = runner.prepare_and_scan(root_folder=EXAMPLES_DIR)

    # then
    assert real_result is not None
    assert runner._check_class == 'mock.mock.MagicMock'
    assert runner._code_repo_path == EXAMPLES_DIR


def test_find_scannable_files():
    # when
    input_paths = Runner().find_scannable_files(
        root_path=EXAMPLES_DIR,
        files=[],
        excluded_paths=set(),
    )

    # then
    assert len(input_paths) == 3

    assert input_paths == {
        EXAMPLES_DIR / "go.sum",
        EXAMPLES_DIR / "package-lock.json",
        EXAMPLES_DIR / "requirements.txt"
    }


def test_find_scannable_files_exclude_go_and_requirements():
    # when
    input_output_paths = Runner().find_scannable_files(
        root_path=EXAMPLES_DIR,
        files=[],
        excluded_paths=set(),
        excluded_file_names=set({"go.sum", "package-lock.json"})
    )

    # then
    assert len(input_output_paths) == 1

    assert input_output_paths == {
        EXAMPLES_DIR / "requirements.txt"
    }


def test_find_scannable_files_with_package_json():
    # when
    input_paths = Runner().find_scannable_files(
        root_path=EXAMPLES_DIR,
        files=[],
        excluded_paths=set(),
        exclude_package_json=False,
    )

    # then
    assert len(input_paths) == 4

    assert input_paths == {
        EXAMPLES_DIR / "go.sum",
        EXAMPLES_DIR / "package.json",
        EXAMPLES_DIR / "package-lock.json",
        EXAMPLES_DIR / "requirements.txt"
    }

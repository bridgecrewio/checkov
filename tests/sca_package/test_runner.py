import os
from pathlib import Path

from mock.mock import MagicMock
from packaging import version as packaging_version
from pytest_mock import MockerFixture

from checkov.common.bridgecrew.platform_integration import bc_integration
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

    # needed till is ready for production use
    mocker.patch.dict(os.environ, {"ENABLE_SCA_PACKAGE_SCAN": "True"})

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
    assert len(report.failed_checks) == 8
    assert len(report.skipped_checks) == 0
    assert len(report.parsing_errors) == 0

    record = next((c for c in report.failed_checks if c.resource == "path/to/go.sum.golang.org/x/crypto"), None)
    assert record is not None
    assert record.bc_check_id == "BC_CVE_2020_29652"
    assert record.check_id == "CKV_CVE_2020_29652"
    assert record.check_class == "mock.mock.MagicMock"  # not the real one
    assert record.check_name == "SCA package scan"
    assert record.check_result == {"result": CheckResult.FAILED}
    assert record.code_block == [(0, "golang.org/x/crypto: v0.0.0-20200622213623-75b288015ac9")]
    assert record.description == (
        "A nil pointer dereference in the golang.org/x/crypto/ssh component through v0.0.0-20201203163018-be400aefbc4c "
        "for Go allows remote attackers to cause a denial of service against SSH servers."
    )
    assert record.file_abs_path == "/path/to/go.sum"
    assert record.file_line_range == [0, 0]
    assert record.file_path == "/path/to/go.sum"
    assert record.repo_file_path == "/path/to/go.sum"
    assert record.resource == "path/to/go.sum.golang.org/x/crypto"
    assert record.severity == "high"
    assert record.short_description == "CVE-2020-29652 - golang.org/x/crypto: v0.0.0-20200622213623-75b288015ac9"
    assert record.vulnerability_details["lowest_fixed_version"] == "v0.0.0-20201216223049-8b5274cf687f"
    assert record.vulnerability_details["fixed_versions"] == [
        packaging_version.parse("v0.0.0-20201216223049-8b5274cf687f"),
    ]


def test_run_with_empty_scan_result(mocker: MockerFixture):
    # given
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    scanner_mock = MagicMock()
    scanner_mock.return_value.scan.return_value = []
    mocker.patch("checkov.sca_package.runner.Scanner", side_effect=scanner_mock)

    # needed till is ready for production use
    mocker.patch.dict(os.environ, {"ENABLE_SCA_PACKAGE_SCAN": "True"})

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

    # needed till is ready for production use
    mocker.patch.dict(os.environ, {"ENABLE_SCA_PACKAGE_SCAN": "True"})

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
    assert len(report.failed_checks) == 7
    assert len(report.skipped_checks) == 1
    assert len(report.parsing_errors) == 0

    record = report.skipped_checks[0]
    assert record.check_id == "CKV_CVE_2020_29652"


def test_find_scannable_files():
    # when
    input_output_paths = Runner().find_scannable_files(
        root_path=EXAMPLES_DIR,
        files=[],
        excluded_paths=set(),
    )

    # then
    assert len(input_output_paths) == 3

    assert input_output_paths == {
        (EXAMPLES_DIR / "go.sum", EXAMPLES_DIR / "go_result.json"),
        (EXAMPLES_DIR / "package-lock.json", EXAMPLES_DIR / "package-lock_result.json"),
        (EXAMPLES_DIR / "requirements.txt", EXAMPLES_DIR / "requirements_result.json"),
    }

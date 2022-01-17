import os
from pathlib import Path

from mock.mock import MagicMock
from pytest_mock import MockerFixture

from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.sca_package.runner import Runner

EXAMPLES_DIR = Path(__file__).parent / "examples"


def test_run(mocker: MockerFixture, scan_result):
    # given
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    scanner_mock = MagicMock()
    # scanner_mock.return_value.__name__ = "Scanner"
    scanner_mock.return_value.scan.return_value = scan_result
    mocker.patch("checkov.sca_package.runner.Scanner", side_effect=scanner_mock)

    # needed till is ready for production use
    mocker.patch.dict(os.environ, {"ENABLE_SCA_PACKAGE_SCAN": "True"})

    # when
    report = Runner().run(root_folder=EXAMPLES_DIR)

    # then
    assert report.check_type == "sca_package"
    assert report.resources == {
        "path/to/go.sum",
        "path/to/sub/requirements.txt",
        "path/to/requirements.txt",
    }
    assert len(report.passed_checks) == 1
    assert len(report.failed_checks) == 2
    assert len(report.skipped_checks) == 0
    assert len(report.parsing_errors) == 0

    go_sum_check = next((c for c in report.failed_checks if c.resource == "go.sum"), None)
    assert go_sum_check is not None
    assert go_sum_check.bc_check_id == "BC_VUL_2"
    assert go_sum_check.check_id == "CKV_VUL_2"
    assert go_sum_check.check_name == "SCA package scan"
    assert go_sum_check.vulnerabilities == {
        "count": {"total": 2, "critical": 0, "high": 2, "medium": 0, "low": 0, "skipped": 0, "fixable": 2},
        "packages": {
            "golang.org/x/crypto": {
                "cves": [
                    {
                        "id": "CVE-2020-29652",
                        "status": "fixed in v0.0.0-20201216223049-8b5274cf687f",
                        "severity": "high",
                        "link": "https://nvd.nist.gov/vuln/detail/CVE-2020-29652",
                        "cvss": 7.5,
                        "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H",
                        "description": "A nil pointer dereference in the golang.org/x/crypto/ssh component through v0.0.0-20201203163018-be400aefbc4c for Go allows remote attackers to cause a denial of service against SSH servers.",
                        "risk_factors": [
                            "Has fix",
                            "High severity",
                            "Attack complexity: low",
                            "Attack vector: network",
                            "DoS",
                        ],
                        "published_date": "2020-12-17T06:15:00+01:00",
                        "fixed_version": "v0.0.0-20201216223049-8b5274cf687f",
                    }
                ],
                "complaint_version": "v0.0.0-20201216223049-8b5274cf687f",
                "current_version": "v0.0.0-20200622213623-75b288015ac9",
            },
            "github.com/dgrijalva/jwt-go": {
                "cves": [
                    {
                        "id": "CVE-2020-26160",
                        "status": "fixed in v4.0.0-preview1",
                        "severity": "high",
                        "link": "https://nvd.nist.gov/vuln/detail/CVE-2020-26160",
                        "cvss": 7.7,
                        "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
                        "description": 'jwt-go before 4.0.0-preview1 allows attackers to bypass intended access restrictions in situations with []string{} for m[\\"aud\\"] (which is allowed by the specification). Because the type assertion fails, \\"\\" is the value of aud. This is a security problem if the JWT token is presented to a service that lacks its own audience check.',
                        "risk_factors": [
                            "High severity",
                            "Attack complexity: low",
                            "Attack vector: network",
                            "Has fix",
                        ],
                        "published_date": "2020-09-30T20:15:00+02:00",
                        "fixed_version": "4.0.0rc1",
                    }
                ],
                "complaint_version": "4.0.0rc1",
                "current_version": "v3.2.0",
            },
        },
    }


def test_run_empty_scan_result(mocker: MockerFixture):
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

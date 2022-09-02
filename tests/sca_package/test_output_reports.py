import xml
from pathlib import Path

from mock.mock import MagicMock
from pytest_mock import MockerFixture

from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.runner_filter import RunnerFilter
from checkov.sca_package.runner import Runner
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.output.csv import CSVSBOM, FILE_NAME_OSS_PACKAGES

EXAMPLES_DIR = Path(__file__).parent / "examples"


def test_console_output(sca_package_report):
    console_output = sca_package_report.print_console(False, False, None, None, False)

    # then
    assert console_output == "\n".join(
        ['\x1b[34msca_package scan results:',
         '\x1b[0m\x1b[36m', 'Failed checks: 9, Skipped checks: 0',
         '',
         '\x1b[0m\t/path/to/requirements.txt - CVEs Summary:',
         '\t┌────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┐',
         '\t│ Total CVEs: 6      │ critical: 1        │ high: 3            │ medium: 2          │ low: 0             │ skipped: 0         │',
         '\t├────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┤',
         '\t│ To fix 6/6 CVEs, go to https://www.bridgecrew.cloud/                                                                        │',
         '\t├────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┤',
         '\t│ Package            │ CVE ID             │ Severity           │ Current version    │ Fixed version      │ Compliant version  │',
         '\t├────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┤',
         '\t│ flask              │ CVE-2019-1010083   │ high               │ 0.6                │ 1.0                │ 1.0                │',
         '\t│                    │ CVE-2018-1000656   │ high               │                    │ 0.12.3             │                    │',
         '\t├────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┤',
         '\t│ django             │ CVE-2019-19844     │ critical           │ 1.2                │ 1.11.27            │ 2.2.24             │',
         '\t│                    │ CVE-2016-7401      │ high               │                    │ 1.8.15             │                    │',
         '\t│                    │ CVE-2016-6186      │ medium             │                    │ 1.8.14             │                    │',
         '\t│                    │ CVE-2021-33203     │ medium             │                    │ 2.2.24             │                    │',
         '\t└────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┘',
         '',
         '\t/path/to/requirements.txt - Licenses Statuses:',
         '\t┌────────────────────────┬────────────────────────┬────────────────────────┬────────────────────────┬─────────────────────────┐',
         '\t│ Package name           │ Package version        │ Policy ID              │ License                │ Status                  │',
         '\t├────────────────────────┼────────────────────────┼────────────────────────┼────────────────────────┼─────────────────────────┤',
         '\t│ flask                  │ 0.6                    │ BC_LIC_1               │ DUMMY_OTHER_LICENSE    │ FAILED                  │',
         '\t└────────────────────────┴────────────────────────┴────────────────────────┴────────────────────────┴─────────────────────────┘',
         '',
         '\t/path/to/go.sum - CVEs Summary:',
         '\t┌────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┐',
         '\t│ Total CVEs: 2      │ critical: 0        │ high: 2            │ medium: 0          │ low: 0             │ skipped: 0         │',
         '\t├────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┤',
         '\t│ To fix 2/2 CVEs, go to https://www.bridgecrew.cloud/                                                                        │',
         '\t├────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┤',
         '\t│ Package            │ CVE ID             │ Severity           │ Current version    │ Fixed version      │ Compliant version  │',
         '\t├────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┤',
         '\t│ golang.org/x/crypt │ CVE-2020-29652     │ high               │ v0.0.1             │ 0.0.2              │ 0.0.2              │',
         '\t│ o                  │                    │                    │                    │                    │                    │',
         '\t├────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┤',
         '\t│ github.com/dgrijal │ CVE-2020-26160     │ high               │ v3.2.0             │ 4.0.0rc1           │ 4.0.0rc1           │',
         '\t│ va/jwt-go          │                    │                    │                    │                    │                    │',
         '\t└────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┘',
         ''])


def test_get_csv_report(sca_package_report, tmp_path: Path):
    csv_sbom_report = CSVSBOM()
    csv_sbom_report.add_report(report=sca_package_report, git_org="acme", git_repository="bridgecrewio/example")
    csv_sbom_report.persist_report_oss_packages(file_name=FILE_NAME_OSS_PACKAGES, is_api_key=True, output_path=str(tmp_path))
    output_file_path = tmp_path / FILE_NAME_OSS_PACKAGES
    csv_output = output_file_path.read_text()
    csv_output_str = csv_sbom_report.get_csv_output_packages(check_type=CheckType.SCA_PACKAGE)

    # then
    expected_csv_output = ['Package,Version,Path,Git Org,Git Repository,Vulnerability,Severity,Licenses',
                           'django,1.2,/path/to/requirements.txt,acme,bridgecrewio/example,CVE-2019-19844,CRITICAL,OSI_BDS',
                           'django,1.2,/path/to/requirements.txt,acme,bridgecrewio/example,CVE-2016-6186,MEDIUM,OSI_BDS',
                           'django,1.2,/path/to/requirements.txt,acme,bridgecrewio/example,CVE-2016-7401,HIGH,OSI_BDS',
                           'django,1.2,/path/to/requirements.txt,acme,bridgecrewio/example,CVE-2021-33203,MEDIUM,OSI_BDS',
                           'flask,0.6,/path/to/requirements.txt,acme,bridgecrewio/example,CVE-2019-1010083,HIGH,"OSI_APACHE, DUMMY_OTHER_LICENSE"',
                           'flask,0.6,/path/to/requirements.txt,acme,bridgecrewio/example,CVE-2018-1000656,HIGH,"OSI_APACHE, DUMMY_OTHER_LICENSE"',
                           'golang.org/x/crypto,v0.0.1,/path/to/go.sum,acme,bridgecrewio/example,CVE-2020-29652,HIGH,Unknown',
                           'github.com/dgrijalva/jwt-go,v3.2.0,/path/to/go.sum,acme,bridgecrewio/example,CVE-2020-26160,HIGH,Unknown',
                           'requests,2.26.0,/path/to/requirements.txt,acme,bridgecrewio/example,,,OSI_APACHE',
                           'requests,2.26.0,/path/to/sub/requirements.txt,acme,bridgecrewio/example,,,OSI_APACHE',
                           'github.com/prometheus/client_model,v0.0.0-20190129233127-fd36f4220a90,/path/to/go.sum,acme,bridgecrewio/example,,,Unknown',
                           'github.com/miekg/dns,v1.1.41,/path/to/go.sum,acme,bridgecrewio/example,,,Unknown',
                           '']
    csv_output_as_list = csv_output.split("\n")
    # the order is not the same always. making sure the header is at the same row
    assert csv_output_as_list[0] == expected_csv_output[0]
    assert set(csv_output_as_list) == set(expected_csv_output)

    expected_csv_output_str = ['Package,Version,Path,Git Org,Git Repository,Vulnerability,Severity,Licenses',
                               '"django",1.2,/path/to/requirements.txt,acme,bridgecrewio/example,CVE-2019-19844,CRITICAL,"OSI_BDS"',
                               '"django",1.2,/path/to/requirements.txt,acme,bridgecrewio/example,CVE-2016-6186,MEDIUM,"OSI_BDS"',
                               '"django",1.2,/path/to/requirements.txt,acme,bridgecrewio/example,CVE-2016-7401,HIGH,"OSI_BDS"',
                               '"django",1.2,/path/to/requirements.txt,acme,bridgecrewio/example,CVE-2021-33203,MEDIUM,"OSI_BDS"',
                               '"flask",0.6,/path/to/requirements.txt,acme,bridgecrewio/example,CVE-2019-1010083,HIGH,"OSI_APACHE, DUMMY_OTHER_LICENSE"',
                               '"flask",0.6,/path/to/requirements.txt,acme,bridgecrewio/example,CVE-2018-1000656,HIGH,"OSI_APACHE, DUMMY_OTHER_LICENSE"',
                               '"golang.org/x/crypto",v0.0.1,/path/to/go.sum,acme,bridgecrewio/example,CVE-2020-29652,HIGH,"Unknown"',
                               '"github.com/dgrijalva/jwt-go",v3.2.0,/path/to/go.sum,acme,bridgecrewio/example,CVE-2020-26160,HIGH,"Unknown"',
                               '"github.com/miekg/dns",v1.1.41,/path/to/go.sum,acme,bridgecrewio/example,,,"Unknown"',
                               '"requests",2.26.0,/path/to/sub/requirements.txt,acme,bridgecrewio/example,,,"OSI_APACHE"',
                               '"github.com/prometheus/client_model",v0.0.0-20190129233127-fd36f4220a90,/path/to/go.sum,acme,bridgecrewio/example,,,"Unknown"',
                               '"requests",2.26.0,/path/to/requirements.txt,acme,bridgecrewio/example,,,"OSI_APACHE"',
                               '']
    csv_output_str_as_list = csv_output_str.split("\n")
    # the order is not the same always. making sure the header is at the same row
    assert csv_output_str_as_list[0] == expected_csv_output_str[0]
    assert set(csv_output_str_as_list) == set(expected_csv_output_str)


def test_get_sarif_json(mocker: MockerFixture, scan_result):
    # given
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    scanner_mock = MagicMock()
    scanner_mock.return_value.scan.return_value = scan_result
    mocker.patch("checkov.sca_package.runner.Scanner", side_effect=scanner_mock)
    runner_filter = RunnerFilter(skip_checks=["CKV_CVE_2020_29652"])

    report = Runner().run(root_folder=EXAMPLES_DIR, runner_filter=runner_filter)

    # when
    sarif_output = report.get_sarif_json("Checkov")

    # then
    sarif_output["runs"][0]["tool"]["driver"]["version"] = "2.0.x"
    assert sarif_output == {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Checkov",
                        "version": "2.0.x",
                        "informationUri": "https://checkov.io",
                        "rules": [
                            {
                                "id": "CKV_CVE_2019_19844",
                                "name": "SCA package scan",
                                "shortDescription": {"text": "CVE-2019-19844 - django: 1.2"},
                                "fullDescription": {
                                    "text": "Django before 1.11.27, 2.x before 2.2.9, and 3.x before 3.0.1 allows account takeover. A suitably crafted email address (that is equal to an existing user\\'s email address after case transformation of Unicode characters) would allow an attacker to be sent a password reset token for the matched user account. (One mitigation in the new releases is to send password reset tokens only to the registered user email address.)"
                                },
                                "help": {
                                    "text": '"SCA package scan\nResource: path/to/requirements.txt.django\nGuideline: None"'
                                },
                                "defaultConfiguration": {"level": "error"},
                            },
                            {
                                "id": "CKV_CVE_2016_6186",
                                "name": "SCA package scan",
                                "shortDescription": {"text": "CVE-2016-6186 - django: 1.2"},
                                "fullDescription": {
                                    "text": "Cross-site scripting (XSS) vulnerability in the dismissChangeRelatedObjectPopup function in contrib/admin/static/admin/js/admin/RelatedObjectLookups.js in Django before 1.8.14, 1.9.x before 1.9.8, and 1.10.x before 1.10rc1 allows remote attackers to inject arbitrary web script or HTML via vectors involving unsafe usage of Element.innerHTML."
                                },
                                "help": {
                                    "text": '"SCA package scan\nResource: path/to/requirements.txt.django\nGuideline: None"'
                                },
                                "defaultConfiguration": {"level": "error"},
                            },
                            {
                                "id": "CKV_CVE_2016_7401",
                                "name": "SCA package scan",
                                "shortDescription": {"text": "CVE-2016-7401 - django: 1.2"},
                                "fullDescription": {
                                    "text": "The cookie parsing code in Django before 1.8.15 and 1.9.x before 1.9.10, when used on a site with Google Analytics, allows remote attackers to bypass an intended CSRF protection mechanism by setting arbitrary cookies."
                                },
                                "help": {
                                    "text": '"SCA package scan\nResource: path/to/requirements.txt.django\nGuideline: None"'
                                },
                                "defaultConfiguration": {"level": "error"},
                            },
                            {
                                "id": "CKV_CVE_2021_33203",
                                "name": "SCA package scan",
                                "shortDescription": {"text": "CVE-2021-33203 - django: 1.2"},
                                "fullDescription": {
                                    "text": "Django before 2.2.24, 3.x before 3.1.12, and 3.2.x before 3.2.4 has a potential directory traversal via django.contrib.admindocs. Staff members could use the TemplateDetailView view to check the existence of arbitrary files. Additionally, if (and only if) the default admindocs templates have been customized by application developers to also show file contents, then not only the existence but also the file contents would have been exposed. In other words, there is directory traversal outside of the template root directories."
                                },
                                "help": {
                                    "text": '"SCA package scan\nResource: path/to/requirements.txt.django\nGuideline: None"'
                                },
                                "defaultConfiguration": {"level": "error"},
                            },
                            {
                                "id": "CKV_CVE_2019_1010083",
                                "name": "SCA package scan",
                                "shortDescription": {"text": "CVE-2019-1010083 - flask: 0.6"},
                                "fullDescription": {
                                    "text": "The Pallets Project Flask before 1.0 is affected by: unexpected memory usage. The impact is: denial of service. The attack vector is: crafted encoded JSON data. The fixed version is: 1. NOTE: this may overlap CVE-2018-1000656."
                                },
                                "help": {
                                    "text": '"SCA package scan\nResource: path/to/requirements.txt.flask\nGuideline: None"'
                                },
                                "defaultConfiguration": {"level": "error"},
                            },
                            {
                                "id": "CKV_CVE_2018_1000656",
                                "name": "SCA package scan",
                                "shortDescription": {"text": "CVE-2018-1000656 - flask: 0.6"},
                                "fullDescription": {
                                    "text": "The Pallets Project flask version Before 0.12.3 contains a CWE-20: Improper Input Validation vulnerability in flask that can result in Large amount of memory usage possibly leading to denial of service. This attack appear to be exploitable via Attacker provides JSON data in incorrect encoding. This vulnerability appears to have been fixed in 0.12.3. NOTE: this may overlap CVE-2019-1010083."
                                },
                                "help": {
                                    "text": '"SCA package scan\nResource: path/to/requirements.txt.flask\nGuideline: None"'
                                },
                                "defaultConfiguration": {"level": "error"},
                            },
                            {
                                "id": "CKV_CVE_2020_26160",
                                "name": "SCA package scan",
                                "shortDescription": {"text": "CVE-2020-26160 - github.com/dgrijalva/jwt-go: v3.2.0"},
                                "fullDescription": {
                                    "text": 'jwt-go before 4.0.0-preview1 allows attackers to bypass intended access restrictions in situations with []string{} for m[\\"aud\\"] (which is allowed by the specification). Because the type assertion fails, \\"\\" is the value of aud. This is a security problem if the JWT token is presented to a service that lacks its own audience check.'
                                },
                                "help": {
                                    "text": '"SCA package scan\nResource: path/to/go.sum.github.com/dgrijalva/jwt-go\nGuideline: None"'
                                },
                                "defaultConfiguration": {"level": "error"},
                            },
                            {
                                "id": "CKV_CVE_2020_29652",
                                "name": "SCA package scan",
                                "shortDescription": {
                                    "text": "CVE-2020-29652 - golang.org/x/crypto: v0.0.1"
                                },
                                "fullDescription": {
                                    "text": "A nil pointer dereference in the golang.org/x/crypto/ssh component through v0.0.3 for Go allows remote attackers to cause a denial of service against SSH servers."
                                },
                                "help": {
                                    "text": '"SCA package scan\nResource: path/to/go.sum.golang.org/x/crypto\nGuideline: None"'
                                },
                                "defaultConfiguration": {"level": "error"},
                            },
                        ],
                        "organization": "bridgecrew",
                    }
                },
                "results": [
                    {
                        "ruleId": "CKV_CVE_2019_19844",
                        "ruleIndex": 0,
                        "level": "error",
                        "message": {
                            "text": "Django before 1.11.27, 2.x before 2.2.9, and 3.x before 3.0.1 allows account takeover. A suitably crafted email address (that is equal to an existing user\\'s email address after case transformation of Unicode characters) would allow an attacker to be sent a password reset token for the matched user account. (One mitigation in the new releases is to send password reset tokens only to the registered user email address.)"
                        },
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": "path/to/requirements.txt"},
                                    "region": {"startLine": 1, "endLine": 1},
                                }
                            }
                        ],
                        "attachments": []
                    },
                    {
                        "ruleId": "CKV_CVE_2016_6186",
                        "ruleIndex": 1,
                        "level": "warning",
                        "message": {
                            "text": "Cross-site scripting (XSS) vulnerability in the dismissChangeRelatedObjectPopup function in contrib/admin/static/admin/js/admin/RelatedObjectLookups.js in Django before 1.8.14, 1.9.x before 1.9.8, and 1.10.x before 1.10rc1 allows remote attackers to inject arbitrary web script or HTML via vectors involving unsafe usage of Element.innerHTML."
                        },
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": "path/to/requirements.txt"},
                                    "region": {"startLine": 1, "endLine": 1},
                                }
                            }
                        ],
                        "attachments": []
                    },
                    {
                        "ruleId": "CKV_CVE_2016_7401",
                        "ruleIndex": 2,
                        "level": "error",
                        "message": {
                            "text": "The cookie parsing code in Django before 1.8.15 and 1.9.x before 1.9.10, when used on a site with Google Analytics, allows remote attackers to bypass an intended CSRF protection mechanism by setting arbitrary cookies."
                        },
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": "path/to/requirements.txt"},
                                    "region": {"startLine": 1, "endLine": 1},
                                }
                            }
                        ],
                        "attachments": []
                    },
                    {
                        "ruleId": "CKV_CVE_2021_33203",
                        "ruleIndex": 3,
                        "level": "warning",
                        "message": {
                            "text": "Django before 2.2.24, 3.x before 3.1.12, and 3.2.x before 3.2.4 has a potential directory traversal via django.contrib.admindocs. Staff members could use the TemplateDetailView view to check the existence of arbitrary files. Additionally, if (and only if) the default admindocs templates have been customized by application developers to also show file contents, then not only the existence but also the file contents would have been exposed. In other words, there is directory traversal outside of the template root directories."
                        },
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": "path/to/requirements.txt"},
                                    "region": {"startLine": 1, "endLine": 1},
                                }
                            }
                        ],
                        "attachments": []
                    },
                    {
                        "ruleId": "CKV_CVE_2019_1010083",
                        "ruleIndex": 4,
                        "level": "error",
                        "message": {
                            "text": "The Pallets Project Flask before 1.0 is affected by: unexpected memory usage. The impact is: denial of service. The attack vector is: crafted encoded JSON data. The fixed version is: 1. NOTE: this may overlap CVE-2018-1000656."
                        },
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": "path/to/requirements.txt"},
                                    "region": {"startLine": 1, "endLine": 1},
                                }
                            }
                        ],
                        "attachments": []
                    },
                    {
                        "ruleId": "CKV_CVE_2018_1000656",
                        "ruleIndex": 5,
                        "level": "error",
                        "message": {
                            "text": "The Pallets Project flask version Before 0.12.3 contains a CWE-20: Improper Input Validation vulnerability in flask that can result in Large amount of memory usage possibly leading to denial of service. This attack appear to be exploitable via Attacker provides JSON data in incorrect encoding. This vulnerability appears to have been fixed in 0.12.3. NOTE: this may overlap CVE-2019-1010083."
                        },
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": "path/to/requirements.txt"},
                                    "region": {"startLine": 1, "endLine": 1},
                                }
                            }
                        ],
                        "attachments": []
                    },
                    {
                        "ruleId": "CKV_CVE_2020_26160",
                        "ruleIndex": 6,
                        "level": "error",
                        "message": {
                            "text": 'jwt-go before 4.0.0-preview1 allows attackers to bypass intended access restrictions in situations with []string{} for m[\\"aud\\"] (which is allowed by the specification). Because the type assertion fails, \\"\\" is the value of aud. This is a security problem if the JWT token is presented to a service that lacks its own audience check.'
                        },
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": "path/to/go.sum"},
                                    "region": {"startLine": 1, "endLine": 1},
                                }
                            }
                        ],
                        "attachments": []
                    },
                    {
                        "ruleId": "CKV_CVE_2020_29652",
                        "ruleIndex": 7,
                        "level": "error",
                        "message": {
                            "text": "A nil pointer dereference in the golang.org/x/crypto/ssh component through v0.0.3 for Go allows remote attackers to cause a denial of service against SSH servers."
                        },
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": "path/to/go.sum"},
                                    "region": {"startLine": 1, "endLine": 1},
                                }
                            }
                        ],
                        "suppressions": [
                            {
                                "kind": "external",
                                "justification": "CVE-2020-29652 is skipped",
                            }
                        ],
                        "attachments": []
                    },
                ],
            }
        ],
    }


def test_get_junit_xml_string(mocker: MockerFixture, scan_result):
    # given
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    scanner_mock = MagicMock()
    scanner_mock.return_value.scan.return_value = scan_result
    mocker.patch("checkov.sca_package.runner.Scanner", side_effect=scanner_mock)
    runner_filter = RunnerFilter(skip_checks=["CKV_CVE_2020_29652"])

    report = Runner().run(root_folder=EXAMPLES_DIR, runner_filter=runner_filter)

    # when
    test_suites = [report.get_test_suite()]
    junit_xml_output = report.get_junit_xml_string(test_suites)

    # then
    assert (
        xml.dom.minidom.parseString(junit_xml_output).toprettyxml()
        == xml.dom.minidom.parseString(
            "".join(
                [
                    '<?xml version="1.0" ?>\n',
                    '<testsuites disabled="0" errors="0" failures="7" tests="8" time="0.0">\n',
                    '\t<testsuite disabled="0" errors="0" failures="7" name="sca_package scan" skipped="1" tests="8" time="0">\n',
                    '\t\t<testcase name="[CRITICAL][CVE-2019-19844] django: 1.2" classname="/path/to/requirements.txt.django" file="/path/to/requirements.txt">\n',
                    '\t\t\t<failure type="failure" message="SCA package scan">\n',
                    "Description: Django before 1.11.27, 2.x before 2.2.9, and 3.x before 3.0.1 allows account takeover. A suitably crafted email address (that is equal to an existing user\\'s email address after case transformation of Unicode characters) would allow an attacker to be sent a password reset token for the matched user account. (One mitigation in the new releases is to send password reset tokens only to the registered user email address.)\n",
                    "Link: https://nvd.nist.gov/vuln/detail/CVE-2019-19844\n",
                    "Published Date: 2019-12-18T20:15:00+01:00\n",
                    "Base Score: 9.8\n",
                    "Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H\n",
                    "Risk Factors: ['Attack complexity: low', 'Attack vector: network', 'Critical severity', 'Has fix']\n",
                    "Fix Details:\n",
                    "  Status: fixed in 3.0.1, 2.2.9, 1.11.27\n",
                    "  Fixed Version: 1.11.27\n",                    
                    "\n",
                    "Resource: path/to/requirements.txt.django\n",
                    "File: /path/to/requirements.txt: 0-0\n",
                    "\n",
                    "\t\t0 | django: 1.2</failure>\n",
                    "\t\t</testcase>\n",
                    '\t\t<testcase name="[MEDIUM][CVE-2016-6186] django: 1.2" classname="/path/to/requirements.txt.django" file="/path/to/requirements.txt">\n',
                    '\t\t\t<failure type="failure" message="SCA package scan">\n',
                    "Description: Cross-site scripting (XSS) vulnerability in the dismissChangeRelatedObjectPopup function in contrib/admin/static/admin/js/admin/RelatedObjectLookups.js in Django before 1.8.14, 1.9.x before 1.9.8, and 1.10.x before 1.10rc1 allows remote attackers to inject arbitrary web script or HTML via vectors involving unsafe usage of Element.innerHTML.\n",
                    "Link: https://nvd.nist.gov/vuln/detail/CVE-2016-6186\n",
                    "Published Date: 2016-08-05T17:59:00+02:00\n",
                    "Base Score: 6.1\n",
                    "Vector: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N\n",
                    "Risk Factors: ['Attack complexity: low', 'Attack vector: network', 'Exploit exists', 'Has fix', 'Medium severity']\n",
                    "Fix Details:\n"
                    "  Status: fixed in 1.9.8, 1.8.14\n",
                    "  Fixed Version: 1.8.14\n",
                    "\n",
                    "Resource: path/to/requirements.txt.django\n",
                    "File: /path/to/requirements.txt: 0-0\n",
                    "\n",
                    "\t\t0 | django: 1.2</failure>\n",
                    "\t\t</testcase>\n",
                    '\t\t<testcase name="[HIGH][CVE-2016-7401] django: 1.2" classname="/path/to/requirements.txt.django" file="/path/to/requirements.txt">\n',
                    '\t\t\t<failure type="failure" message="SCA package scan">\n',
                    "Description: The cookie parsing code in Django before 1.8.15 and 1.9.x before 1.9.10, when used on a site with Google Analytics, allows remote attackers to bypass an intended CSRF protection mechanism by setting arbitrary cookies.\n",
                    "Link: https://nvd.nist.gov/vuln/detail/CVE-2016-7401\n",
                    "Published Date: 2016-10-03T20:59:00+02:00\n",
                    "Base Score: 7.5\n",
                    "Vector: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N\n",
                    "Risk Factors: ['High severity', 'Attack complexity: low', 'Attack vector: network', 'Has fix']\n",
                    "Fix Details:\n",
                    "  Status: fixed in 1.9.10, 1.8.15\n",
                    "  Fixed Version: 1.8.15\n",
                    "\n",
                    "Resource: path/to/requirements.txt.django\n",
                    "File: /path/to/requirements.txt: 0-0\n",
                    "\n",
                    "\t\t0 | django: 1.2</failure>\n",
                    "\t\t</testcase>\n",
                    '\t\t<testcase name="[MEDIUM][CVE-2021-33203] django: 1.2" classname="/path/to/requirements.txt.django" file="/path/to/requirements.txt">\n',
                    '\t\t\t<failure type="failure" message="SCA package scan">\n',
                    "Description: Django before 2.2.24, 3.x before 3.1.12, and 3.2.x before 3.2.4 has a potential directory traversal via django.contrib.admindocs. Staff members could use the TemplateDetailView view to check the existence of arbitrary files. Additionally, if (and only if) the default admindocs templates have been customized by application developers to also show file contents, then not only the existence but also the file contents would have been exposed. In other words, there is directory traversal outside of the template root directories.\n",
                    "Link: https://nvd.nist.gov/vuln/detail/CVE-2021-33203\n",
                    "Published Date: 2021-06-08T20:15:00+02:00\n",
                    "Base Score: 4.9\n",
                    "Vector: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N\n",
                    "Risk Factors: ['Attack complexity: low', 'Attack vector: network', 'Has fix', 'Medium severity', 'Recent vulnerability']\n",
                    "Fix Details:\n"
                    "  Status: fixed in 3.2.4, 3.1.12, 2.2.24\n",
                    "  Fixed Version: 2.2.24\n",
                    "\n",
                    "Resource: path/to/requirements.txt.django\n",
                    "File: /path/to/requirements.txt: 0-0\n",
                    "\n",
                    "\t\t0 | django: 1.2</failure>\n",
                    "\t\t</testcase>\n",
                    '\t\t<testcase name="[HIGH][CVE-2019-1010083] flask: 0.6" classname="/path/to/requirements.txt.flask" file="/path/to/requirements.txt">\n',
                    '\t\t\t<failure type="failure" message="SCA package scan">\n',
                    "Description: The Pallets Project Flask before 1.0 is affected by: unexpected memory usage. The impact is: denial of service. The attack vector is: crafted encoded JSON data. The fixed version is: 1. NOTE: this may overlap CVE-2018-1000656.\n",
                    "Link: https://nvd.nist.gov/vuln/detail/CVE-2019-1010083\n",
                    "Published Date: 2019-07-17T16:15:00+02:00\n",
                    "Base Score: 7.5\n",
                    "Vector: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H\n",
                    "Risk Factors: ['Attack complexity: low', 'Attack vector: network', 'DoS', 'Has fix', 'High severity']\n",
                    "Fix Details:\n"
                    "  Status: fixed in 1.0\n",
                    "  Fixed Version: 1.0\n",
                    "\n",
                    "Resource: path/to/requirements.txt.flask\n",
                    "File: /path/to/requirements.txt: 0-0\n",
                    "\n",
                    "\t\t0 | flask: 0.6</failure>\n",
                    "\t\t</testcase>\n",
                    '\t\t<testcase name="[HIGH][CVE-2018-1000656] flask: 0.6" classname="/path/to/requirements.txt.flask" file="/path/to/requirements.txt">\n',
                    '\t\t\t<failure type="failure" message="SCA package scan">\n',
                    "Description: The Pallets Project flask version Before 0.12.3 contains a CWE-20: Improper Input Validation vulnerability in flask that can result in Large amount of memory usage possibly leading to denial of service. This attack appear to be exploitable via Attacker provides JSON data in incorrect encoding. This vulnerability appears to have been fixed in 0.12.3. NOTE: this may overlap CVE-2019-1010083.\n",
                    "Link: https://nvd.nist.gov/vuln/detail/CVE-2018-1000656\n",
                    "Published Date: 2018-08-20T21:31:00+02:00\n",
                    "Base Score: 7.5\n",
                    "Vector: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H\n",
                    "Risk Factors: ['Attack complexity: low', 'Attack vector: network', 'DoS', 'Has fix', 'High severity']\n",
                    "Fix Details:\n"
                    "  Status: fixed in 0.12.3\n"
                    "  Fixed Version: 0.12.3\n"
                    "\n",
                    "Resource: path/to/requirements.txt.flask\n",
                    "File: /path/to/requirements.txt: 0-0\n",
                    "\n",
                    "\t\t0 | flask: 0.6</failure>\n",
                    "\t\t</testcase>\n",
                    '\t\t<testcase name="[HIGH][CVE-2020-26160] github.com/dgrijalva/jwt-go: v3.2.0" classname="/path/to/go.sum.github.com/dgrijalva/jwt-go" file="/path/to/go.sum">\n',
                    '\t\t\t<failure type="failure" message="SCA package scan">\n',
                    "Description: jwt-go before 4.0.0-preview1 allows attackers to bypass intended access restrictions in situations with []string{} for m[\\&quot;aud\\&quot;] (which is allowed by the specification). Because the type assertion fails, \\&quot;\\&quot; is the value of aud. This is a security problem if the JWT token is presented to a service that lacks its own audience check.\n",
                    "Link: https://nvd.nist.gov/vuln/detail/CVE-2020-26160\n",
                    "Published Date: 2020-09-30T20:15:00+02:00\n",
                    "Base Score: 7.7\n",
                    "Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N\n",
                    "Risk Factors: ['High severity', 'Attack complexity: low', 'Attack vector: network', 'Has fix']\n",
                    "Fix Details:\n"
                    "  Status: fixed in v4.0.0-preview1\n",
                    "  Fixed Version: 4.0.0rc1\n",
                    "\n",
                    "Resource: path/to/go.sum.github.com/dgrijalva/jwt-go\n",
                    "File: /path/to/go.sum: 0-0\n",
                    "\n",
                    "\t\t0 | github.com/dgrijalva/jwt-go: v3.2.0</failure>\n",
                    "\t\t</testcase>\n",
                    '\t\t<testcase name="[HIGH][CVE-2020-29652] golang.org/x/crypto: v0.0.1" classname="/path/to/go.sum.golang.org/x/crypto" file="/path/to/go.sum">\n',
                    '\t\t\t<skipped type="skipped" message="CVE-2020-29652 skipped for golang.org/x/crypto: v0.0.1"/>\n',
                    "\t\t</testcase>\n",
                    "\t</testsuite>\n",
                    "</testsuites>\n",
                ]
            )
        ).toprettyxml()
    )

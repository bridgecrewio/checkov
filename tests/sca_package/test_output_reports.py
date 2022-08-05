import xml
from pathlib import Path

from mock.mock import MagicMock
from pytest_mock import MockerFixture

from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.runner_filter import RunnerFilter
from checkov.sca_package.runner import Runner


EXAMPLES_DIR = Path(__file__).parent / "examples"


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
                                    "text": "CVE-2020-29652 - golang.org/x/crypto: v0.0.0-20200622213623-75b288015ac9"
                                },
                                "fullDescription": {
                                    "text": "A nil pointer dereference in the golang.org/x/crypto/ssh component through v0.0.0-20201203163018-be400aefbc4c for Go allows remote attackers to cause a denial of service against SSH servers."
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
                            "text": "A nil pointer dereference in the golang.org/x/crypto/ssh component through v0.0.0-20201203163018-be400aefbc4c for Go allows remote attackers to cause a denial of service against SSH servers."
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
                    "\n",
                    "Resource: path/to/go.sum.github.com/dgrijalva/jwt-go\n",
                    "File: /path/to/go.sum: 0-0\n",
                    "\n",
                    "\t\t0 | github.com/dgrijalva/jwt-go: v3.2.0</failure>\n",
                    "\t\t</testcase>\n",
                    '\t\t<testcase name="[HIGH][CVE-2020-29652] golang.org/x/crypto: v0.0.0-20200622213623-75b288015ac9" classname="/path/to/go.sum.golang.org/x/crypto" file="/path/to/go.sum">\n',
                    '\t\t\t<skipped type="skipped" message="CVE-2020-29652 skipped for golang.org/x/crypto: v0.0.0-20200622213623-75b288015ac9"/>\n',
                    "\t\t</testcase>\n",
                    "\t</testsuite>\n",
                    "</testsuites>\n",
                ]
            )
        ).toprettyxml()
    )

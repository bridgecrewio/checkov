import os
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock

from typing import Dict, Any, List
from pytest_mock import MockerFixture

import pytest

from checkov.common.bridgecrew.bc_source import SourceType
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration, bc_integration
from checkov.common.output.report import Report
from checkov.sca_package.runner import Runner
from checkov.runner_filter import RunnerFilter

EXAMPLES_DIR = Path(__file__).parent / "examples"

@pytest.fixture(autouse=True)
def mock_env_vars():
    with mock.patch.dict(os.environ, {"CHECKOV_RUN_SCA_PACKAGE_SCAN_V2": "false"}):
        yield


@pytest.fixture()
def mock_bc_integration() -> BcPlatformIntegration:
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    bc_integration.setup_bridgecrew_credentials(
        repo_id="bridgecrewio/checkov",
        skip_fixes=True,
        skip_download=True,
        source=SourceType("Github", False),
        source_version="1.0",
        repo_branch="master",
    )
    return bc_integration


@pytest.fixture()
def scan_result2() -> Dict[str, Any]:
    return {
        "repository": "/tmp/results/requirements.txt",
        "passed": True,
        "packages": [
            {
                "type": "python",
                "name": "django",
                "version": "1.2",
                "path": "/tmp/results/requirements.txt"
            },
            {
                "type": "python",
                "name": "flask",
                "version": "0.6",
                "path": "/tmp/results/requirements.txt"
            },
            {
                "type": "python",
                "name": "requests",
                "version": "2.26.0",
                "path": "/tmp/results/requirements.txt"
            }
        ],
        "complianceIssues": None,
        "complianceDistribution": {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "total": 0
        },
        "vulnerabilities": [
            {
                "id": "CVE-2016-6186",
                "status": "fixed in 1.9.8, 1.8.14",
                "cvss": 6.1,
                "vector": "CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N",
                "description": "Cross-site scripting (XSS) vulnerability in the dismissChangeRelatedObjectPopup function in contrib/admin/static/admin/js/admin/RelatedObjectLookups.js in Django before 1.8.14, 1.9.x before 1.9.8, and 1.10.x before 1.10rc1 allows remote attackers to inject arbitrary web script or HTML via vectors involving unsafe usage of Element.innerHTML.",
                "severity": "medium",
                "packageName": "django",
                "packageVersion": "1.2",
                "link": "https://nvd.nist.gov/vuln/detail/CVE-2016-6186",
                "riskFactors": [
                    "Attack complexity: low",
                    "Attack vector: network",
                    "Exploit exists",
                    "Has fix",
                    "Medium severity"
                ],
                "impactedVersions": [
                    "<=1.8.13"
                ],
                "publishedDate": "2016-08-05T15:59:00Z",
                "discoveredDate": "2016-08-05T15:59:00Z",
                "fixDate": "2016-08-05T15:59:00Z"
            },
            {
                "id": "CVE-2016-7401",
                "status": "fixed in 1.9.10, 1.8.15",
                "cvss": 7.5,
                "vector": "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N",
                "description": "The cookie parsing code in Django before 1.8.15 and 1.9.x before 1.9.10, when used on a site with Google Analytics, allows remote attackers to bypass an intended CSRF protection mechanism by setting arbitrary cookies.",
                "severity": "high",
                "packageName": "django",
                "packageVersion": "1.2",
                "link": "https://nvd.nist.gov/vuln/detail/CVE-2016-7401",
                "riskFactors": [
                    "Attack complexity: low",
                    "Attack vector: network",
                    "Has fix",
                    "High severity"
                ],
                "impactedVersions": [
                    "<=1.8.14"
                ],
                "publishedDate": "2016-10-03T18:59:00Z",
                "discoveredDate": "2016-10-03T18:59:00Z",
                "fixDate": "2016-10-03T18:59:00Z"
            },
            {
                "id": "CVE-2019-19844",
                "status": "fixed in 3.0.1, 2.2.9, 1.11.27",
                "cvss": 9.8,
                "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                "description": "Django before 1.11.27, 2.x before 2.2.9, and 3.x before 3.0.1 allows account takeover. A suitably crafted email address (that is equal to an existing user\\\\\\'s email address after case transformation of Unicode characters) would allow an attacker to be sent a password reset token for the matched user account. (One mitigation in the new releases is to send password reset tokens only to the registered user email address.)",
                "severity": "critical",
                "packageName": "django",
                "packageVersion": "1.2",
                "link": "https://nvd.nist.gov/vuln/detail/CVE-2019-19844",
                "riskFactors": [
                    "Attack complexity: low",
                    "Attack vector: network",
                    "Critical severity",
                    "Has fix"
                ],
                "impactedVersions": [
                    "<1.11.27"
                ],
                "publishedDate": "2019-12-18T19:15:00Z",
                "discoveredDate": "2019-12-18T19:15:00Z",
                "fixDate": "2019-12-18T19:15:00Z"
            },
            {
                "id": "CVE-2021-33203",
                "status": "fixed in 3.2.4, 3.1.12, 2.2.24",
                "cvss": 4.9,
                "vector": "CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N",
                "description": "Django before 2.2.24, 3.x before 3.1.12, and 3.2.x before 3.2.4 has a potential directory traversal via django.contrib.admindocs. Staff members could use the TemplateDetailView view to check the existence of arbitrary files. Additionally, if (and only if) the default admindocs templates have been customized by application developers to also show file contents, then not only the existence but also the file contents would have been exposed. In other words, there is directory traversal outside of the template root directories.",
                "severity": "medium",
                "packageName": "django",
                "packageVersion": "1.2",
                "link": "https://nvd.nist.gov/vuln/detail/CVE-2021-33203",
                "riskFactors": [
                    "Has fix",
                    "Medium severity",
                    "Recent vulnerability",
                    "Attack complexity: low",
                    "Attack vector: network"
                ],
                "impactedVersions": [
                    "<2.2.24"
                ],
                "publishedDate": "2021-06-08T18:15:00Z",
                "discoveredDate": "2021-06-08T18:15:00Z",
                "fixDate": "2021-06-08T18:15:00Z"
            },
            {
                "id": "CVE-2018-1000656",
                "status": "fixed in 0.12.3",
                "cvss": 7.5,
                "vector": "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H",
                "description": "The Pallets Project flask version Before 0.12.3 contains a CWE-20: Improper Input Validation vulnerability in flask that can result in Large amount of memory usage possibly leading to denial of service. This attack appear to be exploitable via Attacker provides JSON data in incorrect encoding. This vulnerability appears to have been fixed in 0.12.3. NOTE: this may overlap CVE-2019-1010083.",
                "severity": "high",
                "packageName": "flask",
                "packageVersion": "0.6",
                "link": "https://nvd.nist.gov/vuln/detail/CVE-2018-1000656",
                "riskFactors": [
                    "Attack complexity: low",
                    "Attack vector: network",
                    "DoS",
                    "Has fix",
                    "High severity"
                ],
                "impactedVersions": [
                    "<0.12.3"
                ],
                "publishedDate": "2018-08-20T19:31:00Z",
                "discoveredDate": "2018-08-20T19:31:00Z",
                "fixDate": "2018-08-20T19:31:00Z"
            },
            {
                "id": "CVE-2019-1010083",
                "status": "fixed in 1.0",
                "cvss": 7.5,
                "vector": "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H",
                "description": "The Pallets Project Flask before 1.0 is affected by: unexpected memory usage. The impact is: denial of service. The attack vector is: crafted encoded JSON data. The fixed version is: 1. NOTE: this may overlap CVE-2018-1000656.",
                "severity": "high",
                "packageName": "flask",
                "packageVersion": "0.6",
                "link": "https://nvd.nist.gov/vuln/detail/CVE-2019-1010083",
                "riskFactors": [
                    "Has fix",
                    "High severity",
                    "Attack complexity: low",
                    "Attack vector: network",
                    "DoS"
                ],
                "impactedVersions": [
                    "<1.0"
                ],
                "publishedDate": "2019-07-17T14:15:00Z",
                "discoveredDate": "2019-07-17T14:15:00Z",
                "fixDate": "2019-07-17T14:15:00Z"
            }
        ],
        "vulnerabilityDistribution": {
            "critical": 1,
            "high": 3,
            "medium": 2,
            "low": 0,
            "total": 6
        }
    }


@pytest.fixture(scope='package')
def scan_result() -> List[Dict[str, Any]]:
    return [
        {
            "repository": "/path/to/requirements.txt",
            "passed": True,
            "packages": [
                {
                    "type": "python",
                    "name": "requests",
                    "version": "2.26.0",
                    "path": "/path/to/requirements.txt",
                },
                {
                    "type": "python",
                    "name": "django",
                    "version": "1.2",
                    "path": "/path/to/requirements.txt",
                },
                {
                    "type": "python",
                    "name": "flask",
                    "version": "0.6",
                    "path": "/path/to/requirements.txt",
                },
            ],
            "complianceIssues": None,
            "complianceDistribution": {"critical": 0, "high": 0, "medium": 0, "low": 0, "total": 0},
            "vulnerabilities": [
                {
                    "id": "CVE-2019-19844",
                    "status": "fixed in 3.0.1, 2.2.9, 1.11.27",
                    "cvss": 9.8,
                    "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                    "description": "Django before 1.11.27, 2.x before 2.2.9, and 3.x before 3.0.1 allows account takeover. A suitably crafted email address (that is equal to an existing user\\'s email address after case transformation of Unicode characters) would allow an attacker to be sent a password reset token for the matched user account. (One mitigation in the new releases is to send password reset tokens only to the registered user email address.)",
                    "severity": "critical",
                    "packageName": "django",
                    "packageVersion": "1.2",
                    "link": "https://nvd.nist.gov/vuln/detail/CVE-2019-19844",
                    "riskFactors": {"Attack complexity: low": {}, "Attack vector: network": {}, "Critical severity": {}, "Has fix": {}},
                    "riskFactorsV2": {
                        "Severity": "Critical",
                        "HasFix": True,
                        "DoS": False,
                        "AttackVector": "network",
                        "AttackComplexity": "low"
                    },
                    "impactedVersions": ["<1.11.27"],
                    "publishedDate": "2019-12-18T20:15:00+01:00",
                    "discoveredDate": "2019-12-18T19:15:00Z",
                    "fixDate": "2019-12-18T20:15:00+01:00",
                },
                {
                    "id": "CVE-2016-6186",
                    "status": "fixed in 1.9.8, 1.8.14",
                    "cvss": 6.1,
                    "vector": "CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N",
                    "description": "Cross-site scripting (XSS) vulnerability in the dismissChangeRelatedObjectPopup function in contrib/admin/static/admin/js/admin/RelatedObjectLookups.js in Django before 1.8.14, 1.9.x before 1.9.8, and 1.10.x before 1.10rc1 allows remote attackers to inject arbitrary web script or HTML via vectors involving unsafe usage of Element.innerHTML.",
                    "severity": "medium",
                    "packageName": "django",
                    "packageVersion": "1.2",
                    "link": "https://nvd.nist.gov/vuln/detail/CVE-2016-6186",
                    "riskFactors": {
                        "Attack complexity: low": {},
                        "Attack vector: network": {},
                        "Medium severity": {},
                        "Has fix": {},
                        "Exploit exists": {}},
                    "riskFactorsV2": {
                        "Severity": "Medium",
                        "HasFix": True,
                        "DoS": False,
                        "AttackVector": "network",
                        "AttackComplexity": "low",
                        "Exploit exists": True
                    },
                    "impactedVersions": ["<=1.8.13"],
                    "publishedDate": "2016-08-05T17:59:00+02:00",
                    "discoveredDate": "2016-08-05T15:59:00Z",
                    "fixDate": "2016-08-05T17:59:00+02:00",
                },
                {
                    "id": "CVE-2016-7401",
                    "status": "fixed in 1.9.10, 1.8.15",
                    "cvss": 7.5,
                    "vector": "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N",
                    "description": "The cookie parsing code in Django before 1.8.15 and 1.9.x before 1.9.10, when used on a site with Google Analytics, allows remote attackers to bypass an intended CSRF protection mechanism by setting arbitrary cookies.",
                    "severity": "high",
                    "packageName": "django",
                    "packageVersion": "1.2",
                    "link": "https://nvd.nist.gov/vuln/detail/CVE-2016-7401",
                    "riskFactors": {"Attack complexity: low": {}, "Attack vector: network": {}, "High severity": {}, "Has fix": {}},
                    "riskFactorsV2": {
                        "Severity": "High",
                        "HasFix": True,
                        "DoS": False,
                        "AttackVector": "network",
                        "AttackComplexity": "low"
                    },
                    "impactedVersions": ["<=1.8.14"],
                    "publishedDate": "2016-10-03T20:59:00+02:00",
                    "discoveredDate": "2016-10-03T18:59:00Z",
                    "fixDate": "2016-10-03T20:59:00+02:00",
                },
                {
                    "id": "CVE-2021-33203",
                    "status": "fixed in 3.2.4, 3.1.12, 2.2.24",
                    "cvss": 4.9,
                    "vector": "CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N",
                    "description": "Django before 2.2.24, 3.x before 3.1.12, and 3.2.x before 3.2.4 has a potential directory traversal via django.contrib.admindocs. Staff members could use the TemplateDetailView view to check the existence of arbitrary files. Additionally, if (and only if) the default admindocs templates have been customized by application developers to also show file contents, then not only the existence but also the file contents would have been exposed. In other words, there is directory traversal outside of the template root directories.",
                    "severity": "medium",
                    "packageName": "django",
                    "packageVersion": "1.2",
                    "link": "https://nvd.nist.gov/vuln/detail/CVE-2021-33203",
                    "riskFactors": {"Attack complexity: low": {}, "Attack vector: network": {}, "High severity": {}, "Has fix": {}},
                    "riskFactorsV2": {
                        "Severity": "High",
                        "HasFix": True,
                        "DoS": False,
                        "AttackVector": "network",
                        "AttackComplexity": "low"
                    },
                    "impactedVersions": ["<2.2.24"],
                    "publishedDate": "2021-06-08T20:15:00+02:00",
                    "discoveredDate": "2021-06-08T18:15:00Z",
                    "fixDate": "2021-06-08T20:15:00+02:00",
                },
                {
                    "id": "CVE-2019-1010083",
                    "status": "fixed in 1.0",
                    "cvss": 7.5,
                    "vector": "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H",
                    "description": "The Pallets Project Flask before 1.0 is affected by: unexpected memory usage. The impact is: denial of service. The attack vector is: crafted encoded JSON data. The fixed version is: 1. NOTE: this may overlap CVE-2018-1000656.",
                    "severity": "high",
                    "packageName": "flask",
                    "packageVersion": "0.6",
                    "link": "https://nvd.nist.gov/vuln/detail/CVE-2019-1010083",
                    "riskFactors": {"Attack complexity: low": {}, "Attack vector: network": {}, "High severity": {},
                                    "Has fix": {}, "Dos": {}},
                    "riskFactorsV2": {
                        "Severity": "High",
                        "HasFix": True,
                        "DoS": True,
                        "AttackVector": "network",
                        "AttackComplexity": "low"
                    },
                    "impactedVersions": ["<1.0"],
                    "publishedDate": "2019-07-17T16:15:00+02:00",
                    "discoveredDate": "2019-07-17T14:15:00Z",
                    "fixDate": "2019-07-17T16:15:00+02:00",
                },
                {
                    "id": "CVE-2018-1000656",
                    "status": "fixed in 0.12.3",
                    "cvss": 7.5,
                    "vector": "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H",
                    "description": "The Pallets Project flask version Before 0.12.3 contains a CWE-20: Improper Input Validation vulnerability in flask that can result in Large amount of memory usage possibly leading to denial of service. This attack appear to be exploitable via Attacker provides JSON data in incorrect encoding. This vulnerability appears to have been fixed in 0.12.3. NOTE: this may overlap CVE-2019-1010083.",
                    "severity": "high",
                    "packageName": "flask",
                    "packageVersion": "0.6",
                    "link": "https://nvd.nist.gov/vuln/detail/CVE-2018-1000656",
                    "riskFactors": {"Attack complexity: low": {}, "Attack vector: network": {}, "High severity": {},
                                    "Has fix": {}, "Dos": {}},
                    "riskFactorsV2": {
                        "Severity": "High",
                        "HasFix": True,
                        "DoS": True,
                        "AttackVector": "network",
                        "AttackComplexity": "low"
                    },
                    "impactedVersions": ["<0.12.3"],
                    "publishedDate": "2018-08-20T21:31:00+02:00",
                    "discoveredDate": "2018-08-20T19:31:00Z",
                    "fixDate": "2018-08-20T21:31:00+02:00",
                },
            ],
            "vulnerabilityDistribution": {"critical": 1, "high": 3, "medium": 2, "low": 0, "total": 6},
            "license_statuses": [
                {
                    "packageName": "django",
                    "packageVersion": "1.2",
                    "packageLang": "python",
                    "license": "OSI_BDS",
                    "status": "COMPLIANT",
                    "policy": "BC_LIC_1"
                },
                {
                    "packageName": "flask",
                    "packageVersion": "0.6",
                    "packageLang": "python",
                    "license": "OSI_APACHE",
                    "status": "COMPLIANT",
                    "policy": "BC_LIC_1"
                },
                {
                    "packageName": "flask",
                    "packageVersion": "0.6",
                    "packageLang": "python",
                    "license": "DUMMY_OTHER_LICENSE",  # not a real license. it is just for test a package with 2 licenses
                    "status": "OPEN",
                    "policy": "BC_LIC_1"
                },
                {
                    "packageName": "requests",
                    "packageVersion": "2.26.0",
                    "packageLang": "python",
                    "license": "OSI_APACHE",
                    "status": "COMPLIANT",
                    "policy": "BC_LIC_1"
                }
            ],
        },
        {
            "repository": "/path/to/sub/requirements.txt",
            "passed": True,
            "packages": [
                {
                    "type": "python",
                    "name": "requests",
                    "version": "2.26.0",
                    "path": "/path/to/sub/requirements.txt",
                }
            ],
            "complianceIssues": None,
            "complianceDistribution": {"critical": 0, "high": 0, "medium": 0, "low": 0, "total": 0},
            "vulnerabilities": None,
            "vulnerabilityDistribution": {"critical": 0, "high": 0, "medium": 0, "low": 0, "total": 0},
            "license_statuses": [
                {
                    "packageName": "requests",
                    "packageVersion": "2.26.0",
                    "packageLang": "python",
                    "license": "OSI_APACHE",
                    "status": "COMPLIANT",
                    "policy": "BC_LIC_1"
                }
            ],
        },
        {
            "repository": "/path/to/go.sum",
            "passed": True,
            "packages": [
                {
                    "type": "go",
                    "name": "github.com/miekg/dns",
                    "version": "v1.1.41",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "golang.org/x/crypto",
                    "version": "v0.0.1",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/dgrijalva/jwt-go",
                    "version": "v3.2.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/prometheus/client_model",
                    "version": "v0.0.0-20190129233127-fd36f4220a90",
                    "path": "/path/to/go.sum",
                }
            ],
            "complianceIssues": None,
            "complianceDistribution": {"critical": 0, "high": 0, "medium": 0, "low": 0, "total": 0},
            "vulnerabilities": [
                {
                    "id": "CVE-2020-29652",
                    "status": "fixed in v0.0.2",
                    "cvss": 7.5,
                    "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H",
                    "description": "A nil pointer dereference in the golang.org/x/crypto/ssh component through v0.0.3 for Go allows remote attackers to cause a denial of service against SSH servers.",
                    "severity": "high",
                    "packageName": "golang.org/x/crypto",
                    "packageVersion": "v0.0.1",
                    "link": "https://nvd.nist.gov/vuln/detail/CVE-2020-29652",
                    "riskFactors": {"Attack complexity: low": {}, "Attack vector: network": {}, "High severity": {},
                                    "Has fix": {}, "Dos": {}},
                    "riskFactorsV2": {
                        "Severity": "High",
                        "HasFix": True,
                        "DoS": True,
                        "AttackVector": "network",
                        "AttackComplexity": "low"
                    },
                    "impactedVersions": ["<v0.0.2"],
                    "publishedDate": "2020-12-17T06:15:00+01:00",
                    "discoveredDate": "2020-12-17T05:15:00Z",
                    "fixDate": "2020-12-17T06:15:00+01:00",
                },
                {
                    "id": "CVE-2020-26160",
                    "status": "fixed in v4.0.0-preview1",
                    "cvss": 7.7,
                    "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
                    "description": 'jwt-go before 4.0.0-preview1 allows attackers to bypass intended access restrictions in situations with []string{} for m[\\"aud\\"] (which is allowed by the specification). Because the type assertion fails, \\"\\" is the value of aud. This is a security problem if the JWT token is presented to a service that lacks its own audience check.',
                    "severity": "high",
                    "packageName": "github.com/dgrijalva/jwt-go",
                    "packageVersion": "v3.2.0",
                    "link": "https://nvd.nist.gov/vuln/detail/CVE-2020-26160",
                    "riskFactors": {"Attack complexity: low": {}, "Attack vector: network": {}, "High severity": {},
                                    "Has fix": {}, "Dos": {}},
                    "riskFactorsV2": {
                        "Severity": "High",
                        "HasFix": True,
                        "DoS": True,
                        "AttackVector": "network",
                        "AttackComplexity": "low"
                    },
                    "impactedVersions": ["<v4.0.0-preview1"],
                    "publishedDate": "2020-09-30T20:15:00+02:00",
                    "discoveredDate": "2020-09-30T18:15:00Z",
                    "fixDate": "2020-09-30T20:15:00+02:00",
                },
            ],
            "vulnerabilityDistribution": {"critical": 0, "high": 2, "medium": 0, "low": 0, "total": 2},
        },
    ]


@pytest.fixture(scope='package')
def scan_result_with_comma_in_licenses() -> List[Dict[str, Any]]:
    return [
        {
            "repository": "/path/to/requirements.txt",
            "passed": True,
            "packages": [
                {
                    "type": "python",
                    "name": "requests",
                    "version": "2.26.0",
                    "path": "/path/to/requirements.txt",
                },
                {
                    "type": "python",
                    "name": "django",
                    "version": "1.2",
                    "path": "/path/to/requirements.txt",
                },
                {
                    "type": "python",
                    "name": "flask",
                    "version": "0.6",
                    "path": "/path/to/requirements.txt",
                },
            ],
            "complianceIssues": None,
            "complianceDistribution": {"critical": 0, "high": 0, "medium": 0, "low": 0, "total": 0},
            "vulnerabilities": [
                {
                    "id": "CVE-2019-19844",
                    "status": "fixed in 3.0.1, 2.2.9, 1.11.27",
                    "cvss": 9.8,
                    "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                    "description": "Django before 1.11.27, 2.x before 2.2.9, and 3.x before 3.0.1 allows account takeover. A suitably crafted email address (that is equal to an existing user\\'s email address after case transformation of Unicode characters) would allow an attacker to be sent a password reset token for the matched user account. (One mitigation in the new releases is to send password reset tokens only to the registered user email address.)",
                    "severity": "critical",
                    "packageName": "django",
                    "packageVersion": "1.2",
                    "link": "https://nvd.nist.gov/vuln/detail/CVE-2019-19844",
                    "riskFactors": ["Attack complexity: low", "Attack vector: network", "Critical severity", "Has fix"],
                    "impactedVersions": ["<1.11.27"],
                    "publishedDate": "2019-12-18T20:15:00+01:00",
                    "discoveredDate": "2019-12-18T19:15:00Z",
                    "fixDate": "2019-12-18T20:15:00+01:00",
                },
                {
                    "id": "CVE-2016-6186",
                    "status": "fixed in 1.9.8, 1.8.14",
                    "cvss": 6.1,
                    "vector": "CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N",
                    "description": "Cross-site scripting (XSS) vulnerability in the dismissChangeRelatedObjectPopup function in contrib/admin/static/admin/js/admin/RelatedObjectLookups.js in Django before 1.8.14, 1.9.x before 1.9.8, and 1.10.x before 1.10rc1 allows remote attackers to inject arbitrary web script or HTML via vectors involving unsafe usage of Element.innerHTML.",
                    "severity": "medium",
                    "packageName": "django",
                    "packageVersion": "1.2",
                    "link": "https://nvd.nist.gov/vuln/detail/CVE-2016-6186",
                    "riskFactors": [
                        "Attack complexity: low",
                        "Attack vector: network",
                        "Exploit exists",
                        "Has fix",
                        "Medium severity",
                    ],
                    "impactedVersions": ["<=1.8.13"],
                    "publishedDate": "2016-08-05T17:59:00+02:00",
                    "discoveredDate": "2016-08-05T15:59:00Z",
                    "fixDate": "2016-08-05T17:59:00+02:00",
                },
                {
                    "id": "CVE-2016-7401",
                    "status": "fixed in 1.9.10, 1.8.15",
                    "cvss": 7.5,
                    "vector": "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N",
                    "description": "The cookie parsing code in Django before 1.8.15 and 1.9.x before 1.9.10, when used on a site with Google Analytics, allows remote attackers to bypass an intended CSRF protection mechanism by setting arbitrary cookies.",
                    "severity": "high",
                    "packageName": "django",
                    "packageVersion": "1.2",
                    "link": "https://nvd.nist.gov/vuln/detail/CVE-2016-7401",
                    "riskFactors": ["High severity", "Attack complexity: low", "Attack vector: network", "Has fix"],
                    "impactedVersions": ["<=1.8.14"],
                    "publishedDate": "2016-10-03T20:59:00+02:00",
                    "discoveredDate": "2016-10-03T18:59:00Z",
                    "fixDate": "2016-10-03T20:59:00+02:00",
                },
                {
                    "id": "CVE-2021-33203",
                    "status": "fixed in 3.2.4, 3.1.12, 2.2.24",
                    "cvss": 4.9,
                    "vector": "CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N",
                    "description": "Django before 2.2.24, 3.x before 3.1.12, and 3.2.x before 3.2.4 has a potential directory traversal via django.contrib.admindocs. Staff members could use the TemplateDetailView view to check the existence of arbitrary files. Additionally, if (and only if) the default admindocs templates have been customized by application developers to also show file contents, then not only the existence but also the file contents would have been exposed. In other words, there is directory traversal outside of the template root directories.",
                    "severity": "medium",
                    "packageName": "django",
                    "packageVersion": "1.2",
                    "link": "https://nvd.nist.gov/vuln/detail/CVE-2021-33203",
                    "riskFactors": [
                        "Attack complexity: low",
                        "Attack vector: network",
                        "Has fix",
                        "Medium severity",
                        "Recent vulnerability",
                    ],
                    "impactedVersions": ["<2.2.24"],
                    "publishedDate": "2021-06-08T20:15:00+02:00",
                    "discoveredDate": "2021-06-08T18:15:00Z",
                    "fixDate": "2021-06-08T20:15:00+02:00",
                },
                {
                    "id": "CVE-2019-1010083",
                    "status": "fixed in 1.0",
                    "cvss": 7.5,
                    "vector": "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H",
                    "description": "The Pallets Project Flask before 1.0 is affected by: unexpected memory usage. The impact is: denial of service. The attack vector is: crafted encoded JSON data. The fixed version is: 1. NOTE: this may overlap CVE-2018-1000656.",
                    "severity": "high",
                    "packageName": "flask",
                    "packageVersion": "0.6",
                    "link": "https://nvd.nist.gov/vuln/detail/CVE-2019-1010083",
                    "riskFactors": [
                        "Attack complexity: low",
                        "Attack vector: network",
                        "DoS",
                        "Has fix",
                        "High severity",
                    ],
                    "impactedVersions": ["<1.0"],
                    "publishedDate": "2019-07-17T16:15:00+02:00",
                    "discoveredDate": "2019-07-17T14:15:00Z",
                    "fixDate": "2019-07-17T16:15:00+02:00",
                },
                {
                    "id": "CVE-2018-1000656",
                    "status": "fixed in 0.12.3",
                    "cvss": 7.5,
                    "vector": "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H",
                    "description": "The Pallets Project flask version Before 0.12.3 contains a CWE-20: Improper Input Validation vulnerability in flask that can result in Large amount of memory usage possibly leading to denial of service. This attack appear to be exploitable via Attacker provides JSON data in incorrect encoding. This vulnerability appears to have been fixed in 0.12.3. NOTE: this may overlap CVE-2019-1010083.",
                    "severity": "high",
                    "packageName": "flask",
                    "packageVersion": "0.6",
                    "link": "https://nvd.nist.gov/vuln/detail/CVE-2018-1000656",
                    "riskFactors": [
                        "Attack complexity: low",
                        "Attack vector: network",
                        "DoS",
                        "Has fix",
                        "High severity",
                    ],
                    "impactedVersions": ["<0.12.3"],
                    "publishedDate": "2018-08-20T21:31:00+02:00",
                    "discoveredDate": "2018-08-20T19:31:00Z",
                    "fixDate": "2018-08-20T21:31:00+02:00",
                },
            ],
            "vulnerabilityDistribution": {"critical": 1, "high": 3, "medium": 2, "low": 0, "total": 6},
            "license_statuses": [
                {
                    "packageName": "django",
                    "packageVersion": "1.2",
                    "packageLang": "python",
                    "license": "OSI_BDS",
                    "status": "COMPLIANT",
                    "policy": "BC_LIC_1"
                },
                {
                    "packageName": "flask",
                    "packageVersion": "0.6",
                    "packageLang": "python",
                    "license": "OSI_APACHE",
                    "status": "COMPLIANT",
                    "policy": "BC_LIC_1"
                },
                {
                    "packageName": "flask",
                    "packageVersion": "0.6",
                    "packageLang": "python",
                    "license": 'DUMMY_OTHER_LICENSE, ANOTHER_DOMMY_LICENSE', # for testing a comma inside licenses
                    "status": "OPEN",
                    "policy": "BC_LIC_1"
                },
                {
                    "packageName": "requests",
                    "packageVersion": "2.26.0",
                    "packageLang": "python",
                    "license": "OSI_APACHE",
                    "status": "COMPLIANT",
                    "policy": "BC_LIC_1"
                }
            ],
        },
        {
            "repository": "/path/to/sub/requirements.txt",
            "passed": True,
            "packages": [
                {
                    "type": "python",
                    "name": "requests",
                    "version": "2.26.0",
                    "path": "/path/to/sub/requirements.txt",
                }
            ],
            "complianceIssues": None,
            "complianceDistribution": {"critical": 0, "high": 0, "medium": 0, "low": 0, "total": 0},
            "vulnerabilities": None,
            "vulnerabilityDistribution": {"critical": 0, "high": 0, "medium": 0, "low": 0, "total": 0},
            "license_statuses": [
                {
                    "packageName": "requests",
                    "packageVersion": "2.26.0",
                    "packageLang": "python",
                    "license": "OSI_APACHE",
                    "status": "COMPLIANT",
                    "policy": "BC_LIC_1"
                }
            ],
        },
        {
            "repository": "/path/to/go.sum",
            "passed": True,
            "packages": [
                {
                    "type": "go",
                    "name": "github.com/miekg/dns",
                    "version": "v1.1.41",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "golang.org/x/crypto",
                    "version": "v0.0.1",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/dgrijalva/jwt-go",
                    "version": "v3.2.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/prometheus/client_model",
                    "version": "v0.0.0-20190129233127-fd36f4220a90",
                    "path": "/path/to/go.sum",
                }
            ],
            "complianceIssues": None,
            "complianceDistribution": {"critical": 0, "high": 0, "medium": 0, "low": 0, "total": 0},
            "vulnerabilities": [
                {
                    "id": "CVE-2020-29652",
                    "status": "fixed in v0.0.2",
                    "cvss": 7.5,
                    "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H",
                    "description": "A nil pointer dereference in the golang.org/x/crypto/ssh component through v0.0.3 for Go allows remote attackers to cause a denial of service against SSH servers.",
                    "severity": "high",
                    "packageName": "golang.org/x/crypto",
                    "packageVersion": "v0.0.1",
                    "link": "https://nvd.nist.gov/vuln/detail/CVE-2020-29652",
                    "riskFactors": [
                        "Has fix",
                        "High severity",
                        "Attack complexity: low",
                        "Attack vector: network",
                        "DoS",
                    ],
                    "impactedVersions": ["<v0.0.2"],
                    "publishedDate": "2020-12-17T06:15:00+01:00",
                    "discoveredDate": "2020-12-17T05:15:00Z",
                    "fixDate": "2020-12-17T06:15:00+01:00",
                },
                {
                    "id": "CVE-2020-26160",
                    "status": "fixed in v4.0.0-preview1",
                    "cvss": 7.7,
                    "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
                    "description": 'jwt-go before 4.0.0-preview1 allows attackers to bypass intended access restrictions in situations with []string{} for m[\\"aud\\"] (which is allowed by the specification). Because the type assertion fails, \\"\\" is the value of aud. This is a security problem if the JWT token is presented to a service that lacks its own audience check.',
                    "severity": "high",
                    "packageName": "github.com/dgrijalva/jwt-go",
                    "packageVersion": "v3.2.0",
                    "link": "https://nvd.nist.gov/vuln/detail/CVE-2020-26160",
                    "riskFactors": ["High severity", "Attack complexity: low", "Attack vector: network", "Has fix"],
                    "impactedVersions": ["<v4.0.0-preview1"],
                    "publishedDate": "2020-09-30T20:15:00+02:00",
                    "discoveredDate": "2020-09-30T18:15:00Z",
                    "fixDate": "2020-09-30T20:15:00+02:00",
                },
            ],
            "vulnerabilityDistribution": {"critical": 0, "high": 2, "medium": 0, "low": 0, "total": 2},
        },
    ]


@pytest.fixture()
@mock.patch.dict(os.environ, {'CHECKOV_RUN_SCA_PACKAGE_SCAN_V2': 'false'})
def scan_result_success_response() -> Dict[str, Any]:
    return {'outputType': 'Result',
     'outputData': "H4sIAN22X2IC/8WY23LbOBKGX6VLN5tUWRQp"
                   "+SCrZi88drL2VqKkLMUzNZu5gEjIQkwSXAKUrU3l3fdvgDofnNS4MheJKbIJdAP"
                   "/193g10YpC22U1eWs0aNGy2ZFq5SmSq3B3/9WqpSZzK0J7JNtHFGjEMbIBKa2rKT7HT"
                   "+Ie2lw5z9fG3ZWSB6mmNmJztk+F5m7k3wR+b3mO1NZGoWHuBkFbT+mnTw"
                   "/+bcjOjTBOBXmYWP8MDh9sfHZXhprNqZoB+3TIPyBWf6EaayzIlUij"
                   "+WNMZVbvLxK07UnV8rYUo0q6yf62ohLZVUsUvwIYTlR95P6MpOJqrL6R6of6yurrbf+xi5XaS5LMVIpRplvl"
                   "+KNbFzevWm2w+i0eRp13XoZK2xl3KKqJ5mQyikKzoPuEf50g+iYbeKpYYvTIHLrEUNAfqzBoNcJwtbFXa"
                   "/furjsvWt9vMXVp5vebWvQu2zxnRv8u+j1eZhEGsRV1EE2LkttTBNylFTfz+/p1e"
                   "+DwWtaDWDGLtmJpESZTBlzOYG45K1MhZXJh9EXuPNRF1VB4yqPeWy2j3XOC9oSSabyFseo4vrHF1NfrA3x"
                   "TuuHqjDBF8OvXzkB00iOdSnrhThy6/K0vOkWSeQJLqNw9UEUlnFEIsXuGIIeNCIU1gIeSImsxgw8JYlypGw"
                   "pyhk9ylG9BqRLuh6+f0dTJcgvNXs01emUl6fKjRhLqgwwJD2mN6mTW6ByrBe/F7g9lRAtVo5XudbLkt7+Fq"
                   "T1g7stVlOVP/DPibWF6bVa+TQJckg1uNfTFu9RK5FWqLS1papSmYe3wnnP6mtcuPDJKV4+wbUesXZhWT/xoQ"
                   "INaR916dh+81SkWlmCfY3itTAElfLlexcWLSJl0lSGSLCjdSB+5l/+6bav4yyKapQqM5HJFXbeEc1Oh91meD"
                   "KMTnon570w/MNJVZlYY+jnLeHPQROXaTbYOzsOowPsRWEN38kKfGfByffC1wd8nwBfH/Bd74FvCKBiaF5JKgS"
                   "WC9qKdSL3iP+k1vmG/tnRx4nMoUd4D/IEOZwflZ3Qv7S+TyVd5CKdgT5zdIiI0YxrDWaBA1bmCYa7HNy+paKE"
                   "qac6kzHIRw6AMfbdunSxRMgHY7b071LnT1L/fF9fQv0rWr9GCN+v9OMDSo/CZtgZRt3nlb7DclPpmybbSj9vR"
                   "ufd4+M9Uod4uaCgqAbnLPgI6362oniXX7cVHx1Q/HWt+Osdit+UtZuOp19IuvaEpd5Z3nVuzrUr4lhXuSUrHi"
                   "SvWkAXZCplxSiFBEsxxqaQzKAKEkmCxsDQKzsRlpQhdAciZbFD5S6nuYRuZPn58z/Mxks8UEmxMBK9l8gNPMmE"
                   "wwBJ/1OuHKvgoWQZlOY1PeoqTbyXPP4cLscW6itqBOBkxqCvBAgCIDx7ALsY2pVXjB9DL86jeZwBvfqQ4xHaiH"
                   "sxr61snMtHDJJKOGg4NkyDOZKdMxhkBqwOTPjNUt4jdNabn2kt7uD1Jr6LRuinILwi2Jdg+LJ2fgnvCtj7OZ6js"
                   "I9jeNluRt1hdN5DnTnE8U7LdY63TbY4bkfNTqcddvZy3A7QHYHMIGp7nturbeMxQ/Usx9ebHPf3VK51jv1sR+vA"
                   "ekc8x+3VB3CUJlh/oIC6kluFvUnQsrNrMyaNm33c4+bLyyuoO8nA9YyJjk1AAyvGY9SjbMTVK3bkVUwq5D2U0Ad"
                   "W98rp6k6Bkyn/B/WDLsiEjRz9En0/07wsYWOVooDRRZIoDhYwz45IjekVR+IYUuPXvhWWY4EjBy2cIlvPaxDfVC"
                   "JikB1XxupM/Q/bhJIpChw2Yk9xAj2muqiLr0gN8J0gc7AHrnfmI8wRT5VTrm0N8JrnOKz4F/n22nt1Llr6IZ9w6p"
                   "RJQDdIXzAviVOEHx/bgvSxaw90ZY1K3BLxFPMAqdRwaP7Cror/EzveVTJeuOhvNri4dStjzuNrh6MDaaQGcU8Wge"
                   "shd6tcwA9nkd2Wa1lkh8l2N9BFxxCGpyf7jp0os+2g89db3v6eBoBb3o+ASkKiH0vtjmDuQwLVR3z61ecJ74jTs1"
                   "A5Z4vL3ziCHt1kaEiBDZRcQP93IlWJJ2rrxOpHdrU/RkH23wj4wTtR4uwmMtdHaJdHWPj+SAdQjOJeAqU14f4AeC"
                   "Yy5zwFU9TLqYplQMMJoPE1nrmWYl7opT8zoR2RLoldzPsA+D0FTYb+PfjQJzgt2BeVx7pkkghMa56wHns9HD+Fyx"
                   "VLqjf2LaD+h+GbHiLG65mYEcsoFQUtS2uI/e92vrdDX3zj2Ya1/tTzo9V9TYB7cN0B5ZUeHGzIl0Rvsr6fzVrr+y"
                   "p8l4+R7ZCLcic6WOF3Wq5X+G2TnZ263529x9Lw54L51uGzaNZDrhKoupKXEtWsR1UOrfufqwSxflFS3KLjnd5ueu"
                   "anz3q7neGie2cS8HcBin/BL8U8U/AL0XOSX+jt75P82r6+RIV6DoZDXW14oKMNz5rR2TA6fr6j3WG52dFumrjvsG"
                   "sp7dAH12j5wbWz+sG1vfOD6+m3b/8HQd/FwVgXAAA=",
     'compressionMethod': 'gzip'}


@pytest.fixture(scope='package')
@mock.patch.dict(os.environ, {'CHECKOV_RUN_SCA_PACKAGE_SCAN_V2': 'false'})
def sca_package_report(package_mocker: MockerFixture, scan_result: List[Dict[str, Any]]) -> Report:
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    scanner_mock = MagicMock()
    scanner_mock.return_value.scan.return_value = scan_result
    package_mocker.patch("checkov.sca_package.runner.Scanner", side_effect=scanner_mock)

    return Runner().run(root_folder=EXAMPLES_DIR)

@pytest.fixture(scope='package')
def sca_package_report_with_comma_in_licenses(package_mocker: MockerFixture, scan_result_with_comma_in_licenses: List[Dict[str, Any]]) -> Report:
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    scanner_mock = MagicMock()
    scanner_mock.return_value.scan.return_value = scan_result_with_comma_in_licenses
    package_mocker.patch("checkov.sca_package.runner.Scanner", side_effect=scanner_mock)

    package_mocker.patch.dict(os.environ, {'CHECKOV_RUN_SCA_PACKAGE_SCAN_V2': 'false'})
    return Runner().run(root_folder=EXAMPLES_DIR)


def get_sca_package_report_with_skip(package_mocker: MockerFixture, scan_result: List[Dict[str, Any]]) -> Report:
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    scanner_mock = MagicMock()
    scanner_mock.return_value.scan.return_value = scan_result
    package_mocker.patch("checkov.sca_package.runner.Scanner", side_effect=scanner_mock)
    runner_filter = RunnerFilter(skip_checks=["CKV_CVE_2020_29652"])

    return Runner().run(root_folder=EXAMPLES_DIR, runner_filter=runner_filter)


@pytest.fixture(scope='package')
def sca_package_report_with_skip(package_mocker: MockerFixture, scan_result: List[Dict[str, Any]]) -> Report:
    return get_sca_package_report_with_skip(package_mocker, scan_result)


@pytest.fixture(scope='function')
def sca_package_report_with_skip_scope_function(package_mocker: MockerFixture, scan_result: List[Dict[str, Any]]) -> Report:
    return get_sca_package_report_with_skip(package_mocker, scan_result)

import os
from pathlib import Path
from unittest import mock

from mock.mock import MagicMock
from typing import Dict, Any, List
from pytest_mock import MockerFixture

import pytest

os.environ['CHECKOV_RUN_SCA_PACKAGE_SCAN_V2'] = 'true'

from checkov.common.bridgecrew.bc_source import SourceType
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration, bc_integration
from checkov.common.output.report import Report
from checkov.sca_package_2.runner import Runner
from checkov.runner_filter import RunnerFilter

EXAMPLES_DIR = Path(__file__).parent / "examples"


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


@pytest.fixture(scope='package')
def scan_result_2() -> Dict[str, Dict[str, Any]]:
    return {
        "/path/to/requirements.txt": {
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
                    "license": "DUMMY_OTHER_LICENSE",
                    # not a real license. it is just for test a package with 2 licenses
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
        "/path/to/sub/requirements.txt": {
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
        "/path/to/go.sum": {
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
        }
    }


@pytest.fixture(scope='package')
def scan_result_2_with_comma_in_licenses() -> Dict[str, Any]:
    return {
        "/path/to/requirements.txt": {
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
                    "license": 'DUMMY_OTHER_LICENSE, ANOTHER_DOMMY_LICENSE',  # for testing a comma inside licenses
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
        "/path/to/sub/requirements.txt": {
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
        "/path/to/go.sum": {
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
        }, }


@pytest.fixture()
@mock.patch.dict(os.environ, {'CHECKOV_RUN_SCA_PACKAGE_SCAN_V2': 'true'})
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
@mock.patch.dict(os.environ, {'CHECKOV_RUN_SCA_PACKAGE_SCAN_V2': 'true'})
def sca_package_2_report(package_mocker: MockerFixture, scan_result_2: Dict[str, Any]) -> Report:
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    scanner_mock = MagicMock()
    scanner_mock.return_value.scan.return_value = scan_result_2
    package_mocker.patch("checkov.sca_package_2.runner.Scanner", side_effect=scanner_mock)

    return Runner().run(root_folder=EXAMPLES_DIR)


@pytest.fixture(scope='package')
def sca_package_report_2_with_comma_in_licenses(package_mocker: MockerFixture,
                                                scan_result_2_with_comma_in_licenses: List[Dict[str, Any]]) -> Report:
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    scanner_mock = MagicMock()
    scanner_mock.return_value.scan.return_value = scan_result_2_with_comma_in_licenses
    package_mocker.patch("checkov.sca_package_2.runner.Scanner", side_effect=scanner_mock)
    package_mocker.patch.dict(os.environ, {'CHECKOV_RUN_SCA_PACKAGE_SCAN_V2': 'true'})
    return Runner().run(root_folder=EXAMPLES_DIR)


def get_sca_package_2_report_with_skip(package_mocker: MockerFixture, scan_result_2: List[Dict[str, Any]]) -> Report:
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    scanner_mock = MagicMock()
    scanner_mock.return_value.scan.return_value = scan_result_2
    package_mocker.patch("checkov.sca_package_2.runner.Scanner", side_effect=scanner_mock)
    runner_filter = RunnerFilter(skip_checks=["CKV_CVE_2020_29652"])

    return Runner().run(root_folder=EXAMPLES_DIR, runner_filter=runner_filter)


@pytest.fixture(scope='package')
def sca_package_2_report_with_skip(package_mocker: MockerFixture, scan_result_2: List[Dict[str, Any]]) -> Report:
    return get_sca_package_2_report_with_skip(package_mocker, scan_result_2)


@pytest.fixture(scope='function')
def sca_package_report_2_with_skip_scope_function(package_mocker: MockerFixture,
                                                  scan_result_2: List[Dict[str, Any]]) -> Report:
    return get_sca_package_2_report_with_skip(package_mocker, scan_result_2)


def get_vulnerabilities_details_package_json() -> List[Dict[str, Any]]:
    return [
        {'details': {'cveId': 'PRISMA-2021-0070', 'severity': 'medium', 'packageName': 'cypress',
                     'packageVersion': '3.8.3', 'link': '', 'cvss': 0, 'vector': '',
                     'description': '', 'riskFactors': {}, 'publishedDate': '',
                     'status': 'fixed in 7.2.0', 'lowest_fixed_version': '7.2.0'},
         'root_package_version': '3.8.3', 'root_package_name': 'cypress'},
        {'details': {'cveId': 'CVE-2021-44906', 'severity': 'critical', 'packageName': 'minimist',
                     'packageVersion': '1.2.5',
                     'link': '', 'cvss': 9.8,
                     'vector': '',
                     'description': '',
                     'riskFactors': {},
                     'publishedDate': '', 'status': 'fixed in 1.2.6'}, 'root_package_name': 'forever',
         'root_package_version': '2.0.0'},
        {'details': {'cveId': 'CVE-2022-21803', 'severity': 'high', 'packageName': 'nconf', 'packageVersion': '0.6.9',
                     'link': '', 'cvss': 7.5, 'vector': '',
                     'description': '',
                     'riskFactors': {},
                     'publishedDate': '', 'status': 'fixed in 0.11.4'}, 'root_package_name': 'forever',
         'root_package_version': '2.0.0'},
        {'details': {'cveId': 'CVE-2020-7598', 'severity': 'medium', 'packageName': 'minimist',
                     'packageVersion': '0.0.10',
                     'link': '', 'cvss': 5.6,
                     'vector': '',
                     'description': '',
                     'riskFactors': {},
                     'publishedDate': '', 'status': 'fixed in 1.2.2',
                     }, 'root_package_name': 'forever', 'root_package_version': '2.0.0'},
        {'details': {'cveId': 'CVE-2021-44906', 'severity': 'critical', 'packageName': 'minimist',
                     'packageVersion': '0.0.10',
                     'link': '', 'cvss': 9.8,
                     'vector': '',
                     'description': '',
                     'riskFactors': {},
                     'publishedDate': '', 'status': 'fixed in 1.2.6'}, 'root_package_name': 'forever',
         'root_package_version': '2.0.0'},
        {'details': {'cveId': 'PRISMA-2022-0049', 'severity': 'high', 'packageName': 'unset-value',
                     'packageVersion': '1.0.0',
                     'link': '',
                     'cvss': 8, 'vector': '',
                     'description': '',
                     'riskFactors': {}, 'status': 'fixed in 2.0.1',
                     'publishedDate': ''}, 'root_package_name': 'forever',
         'root_package_version': '2.0.0'},
        {'details': {'cveId': 'CVE-2020-28469', 'severity': 'high', 'packageName': 'glob-parent',
                     'packageVersion': '3.1.0',
                     'link': '', 'cvss': 7.5,
                     'vector': '',
                     'description': '',
                     'riskFactors': {}, 'publishedDate': '', 'status': 'fixed in 5.1.2'},
         'root_package_name': 'forever', 'root_package_version': '2.0.0'},
        {'details': {'cveId': 'CVE-2022-38900', 'severity': 'low', 'packageName': 'decode-uri-component',
                     'packageVersion': '0.2.0',
                     'link': '', 'cvss': 1,
                     'vector': '',
                     'description': '',
                     'riskFactors': {}, 'publishedDate': '', 'status': 'fixed in 0.2.1'},
         'root_package_name': 'forever', 'root_package_version': '2.0.0'},
        {'details': {'cveId': 'CVE-2022-21803', 'severity': 'high', 'packageName': 'nconf', 'packageVersion': '0.10.0',
                     'link': '', 'cvss': 7.5,
                     'vector': '',
                     'description': '',
                     'riskFactors': {},
                     'publishedDate': '', 'status': 'fixed in 0.11.4'}, 'root_package_name': 'forever',
         'root_package_version': '2.0.0'},
        {'details': {'cveId': 'CVE-2022-1537', 'severity': 'high', 'packageName': 'grunt', 'packageVersion': '1.4.1',
                     'link': '', 'cvss': 7,
                     'vector': '',
                     'description': '',
                     'riskFactors': {},
                     'publishedDate': '', 'status': 'fixed in 1.5.3'}, 'root_package_name': 'grunt',
         'root_package_version': '1.4.1'},
        {'details': {'cveId': 'CVE-2022-0436', 'severity': 'medium', 'packageName': 'grunt', 'packageVersion': '1.4.1',
                     'link': '', 'cvss': 5.5,
                     'vector': '',
                     'description': '',
                     'riskFactors': {}, 'publishedDate': '', 'status': 'fixed in 1.5.2'},
         'root_package_name': 'grunt', 'root_package_version': '1.4.1'},
        {'details': {'cveId': 'CVE-2017-16137', 'severity': 'medium', 'packageName': 'debug', 'packageVersion': '2.2.0',
                     'link': '', 'cvss': 5.3,
                     'vector': '',
                     'description': '',
                     'riskFactors': {}, 'publishedDate': '', 'status': 'fixed in 3.1.0, 2.6.9'},
         'root_package_name': 'helmet', 'root_package_version': '2.3.0'},
        {'details': {'cveId': 'GHSA-C3M8-X3CG-QM2C', 'severity': 'medium', 'packageName': 'helmet-csp',
                     'packageVersion': '1.2.2', 'link': '', 'cvss': 4, 'vector': '',
                     'description': '',
                     'riskFactors': {}, 'publishedDate': '', 'status': 'fixed in 2.9.1'},
         'root_package_name': 'helmet', 'root_package_version': '2.3.0'},
        {'details': {'cveId': 'PRISMA-2021-0013', 'severity': 'medium', 'packageName': 'marked',
                     'packageVersion': '0.3.9',
                     'link': '', 'cvss': 0, 'vector': '',
                     'description': '',
                     'riskFactors': {},
                     'publishedDate': '', 'status': 'fixed in 1.1.1'}, 'root_package_name': 'marked',
         'root_package_version': '0.3.9'},
        {'details': {'cveId': 'CVE-2022-21681', 'severity': 'high', 'packageName': 'marked', 'packageVersion': '0.3.9',
                     'link': '', 'cvss': 7.5,
                     'vector': '',
                     'description': '',
                     'riskFactors': {},
                     'publishedDate': '', 'status': 'fixed in 4.0.10'}, 'root_package_name': 'marked',
         'root_package_version': '0.3.9'},
        {'details': {'cveId': 'CVE-2022-21680', 'severity': 'high', 'packageName': 'marked', 'packageVersion': '0.3.9',
                     'link': '', 'cvss': 7.5,
                     'vector': '',
                     'description': '',
                     'riskFactors': {},
                     'publishedDate': '', 'status': 'fixed in 4.0.10'}, 'root_package_name': 'marked',
         'root_package_version': '0.3.9'},
        {'details': {'cveId': 'PRISMA-2022-0230', 'severity': 'high', 'packageName': 'mocha', 'packageVersion': '2.5.3',
                     'link': '', 'cvss': 7.5, 'vector': '',
                     'description': '',
                     'riskFactors': {}, 'publishedDate': '', 'status': 'open'},
         'root_package_name': 'mocha', 'root_package_version': '2.5.3'},
        {'details': {'cveId': 'PRISMA-2022-0335', 'severity': 'medium', 'packageName': 'mocha',
                     'packageVersion': '2.5.3',
                     'link': '',
                     'cvss': 5.3, 'vector': '',
                     'description': '',
                     'riskFactors': {}, 'publishedDate': '', 'status': 'open'},
         'root_package_name': 'mocha', 'root_package_version': '2.5.3'},
        {'details': {'cveId': 'GHSA-MH5C-679W-HH4R', 'severity': 'high', 'packageName': 'mongodb',
                     'packageVersion': '2.2.36',
                     'link': '', 'cvss': 7, 'vector': '', 'description': '',
                     'riskFactors': {},
                     'publishedDate': '', 'status': 'fixed in 3.1.13'}, 'root_package_name': 'mongodb',
         'root_package_version': '2.2.36'},
        {'details': {'cveId': 'CVE-2019-2391', 'severity': 'medium', 'packageName': 'bson', 'packageVersion': '1.0.9',
                     'link': '', 'cvss': 4, 'vector': '', 'description': '',
                     'riskFactors': {}, 'publishedDate': '', 'status': 'fixed in 1.1.4'
                     }, 'root_package_name': 'mongodb', 'root_package_version': '2.2.36'},
        {'details': {'cveId': 'CVE-2020-7610', 'severity': 'critical', 'packageName': 'bson', 'packageVersion': '1.0.9',
                     'link': '', 'cvss': 9.8,
                     'vector': '',
                     'description': '',
                     'riskFactors': {}, 'publishedDate': '', 'status': 'fixed in 1.1.4'
                     }, 'root_package_name': 'mongodb', 'root_package_version': '2.2.36'},
        {'details': {'cveId': 'CVE-2020-7598', 'severity': 'medium', 'packageName': 'minimist',
                     'packageVersion': '0.0.10',
                     'link': '', 'cvss': 5.6, 'vector': '', 'description': '',
                     'riskFactors': {},
                     'publishedDate': '', 'status': 'fixed in 1.2.2'}, 'root_package_name': 'swig',
         'root_package_version': '1.4.2'},
        {'details': {'cveId': 'CVE-2021-44906', 'severity': 'critical', 'packageName': 'minimist',
                     'packageVersion': '0.0.10',
                     'link': '', 'cvss': 9.8,
                     'vector': '',
                     'description': '',
                     'riskFactors': {},
                     'publishedDate': '', 'status': 'fixed in 1.2.6'}, 'root_package_name': 'swig',
         'root_package_version': '1.4.2'},
        {'details': {'cveId': 'PRISMA-2021-0169', 'severity': 'medium', 'packageName': 'uglify-js',
                     'packageVersion': '2.4.24', 'link': '',
                     'cvss': 5.3, 'vector': '',
                     'description': '',
                     'riskFactors': {},
                     'publishedDate': '', 'status': 'fixed in 3.14.3'}, 'root_package_name': 'swig',
         'root_package_version': '1.4.2'},
        {'details': {'cveId': 'CVE-2015-8858', 'severity': 'high', 'packageName': 'uglify-js',
                     'packageVersion': '2.4.24',
                     'link': '', 'cvss': 7,
                     'vector': '',
                     'description': '',
                     'riskFactors': {}, 'publishedDate': '', 'status': 'fixed in 2.6.0'},
         'root_package_name': 'swig', 'root_package_version': '1.4.2'}
    ]


def get_vulnerabilities_details() -> List[Dict[str, Any]]:
    return [
        {
            "id": "CVE-2019-19844",
            "status": "fixed in 3.0.1, 2.2.9, 1.11.27",
            "cvss": 9.8,
            "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
            "description": "Django before 1.11.27, 2.x before 2.2.9, and 3.x before 3.0.1 allows account takeover. ...",
            "severity": "critical",
            "packageName": "django",
            "packageVersion": "1.2",
            "link": "https://nvd.nist.gov/vuln/detail/CVE-2019-19844",
            "riskFactors": [
                "Attack complexity: low",
                "Attack vector: network",
                "Critical severity",
                "Has fix",
            ],
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
            "description": "Cross-site scripting (XSS) vulnerability in the dismissChangeRelatedObjectPopup function ...",
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
    ]


def get_vulnerabilities_details_no_deps() -> List[Dict[str, Any]]:
    return [{'cveId': 'PRISMA-2021-0013', 'status': 'fixed in 1.1.1', 'severity': 'medium', 'packageName': 'marked',
             'packageVersion': '0.3.9', 'link': None, 'cvss': None, 'vector': None,
             'description': 'marked package prior to 1.1.1 are vulnerable to  Regular Expression Denial of Service (ReDoS). The regex within src/rules.js file have multiple unused capture groups which could lead to a denial of service attack if user input is reachable.  Origin: https://github.com/markedjs/marked/commit/bd4f8c464befad2b304d51e33e89e567326e62e0',
             'riskFactors': ['DoS', 'Has fix', 'Medium severity'], 'publishedDate': '2021-01-14T10:29:35Z'},
            {'cveId': 'CVE-2022-21681', 'status': 'fixed in 4.0.10', 'severity': 'high', 'packageName': 'marked',
             'packageVersion': '0.3.9', 'link': 'https://github.com/advisories/GHSA-5v2h-r2cx-5xgj', 'cvss': 7.5,
             'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H',
             'description': 'Marked is a markdown parser and compiler. Prior to version 4.0.10, the regular expression `inline.reflinkSearch` may cause catastrophic backtracking against some strings and lead to a denial of service (DoS). Anyone who runs untrusted markdown through a vulnerable version of marked and does not use a worker with a time limit may be affected. This issue is patched in version 4.0.10. As a workaround, avoid running untrusted markdown through marked or run marked on a worker thread and set a reasonable time limit to prevent draining resources.',
             'riskFactors': ['DoS', 'Has fix', 'High severity', 'Recent vulnerability', 'Attack complexity: low',
                             'Attack vector: network'], 'publishedDate': '2022-01-14T17:15:00Z'},
            {'cveId': 'CVE-2022-21680', 'status': 'fixed in 4.0.10', 'severity': 'high', 'packageName': 'marked',
             'packageVersion': '0.3.9', 'link': 'https://github.com/advisories/GHSA-rrrm-qjm4-v8hf', 'cvss': 7.5,
             'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H',
             'description': 'Marked is a markdown parser and compiler. Prior to version 4.0.10, the regular expression `block.def` may cause catastrophic backtracking against some strings and lead to a regular expression denial of service (ReDoS). Anyone who runs untrusted markdown through a vulnerable version of marked and does not use a worker with a time limit may be affected. This issue is patched in version 4.0.10. As a workaround, avoid running untrusted markdown through marked or run marked on a worker thread and set a reasonable time limit to prevent draining resources.',
             'riskFactors': ['Has fix', 'High severity', 'Recent vulnerability', 'Attack complexity: low',
                             'Attack vector: network', 'DoS'], 'publishedDate': '2022-01-14T17:15:00Z'}
            ]

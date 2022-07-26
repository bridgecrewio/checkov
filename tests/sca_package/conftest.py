from typing import Dict, Any, List

import pytest

from checkov.common.bridgecrew.bc_source import SourceType
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration, bc_integration


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
        },
        'license_data': [{
            'packageName': 'github.com/armon/go-metrics',
            'packageVers ion': 'v0.0.0-20180917152333-f0300d1749da',
            'packageLang': 'go',
            'license': 'PRIVATE',
            'status': 'OPEN',
            'policy': 'BC_LIC_1'
        }, {
            'packageName': 'github.com/chzyer/readline',
            'packageVersion': 'v0.0.0-20180603132655-2972be24d48e',
            'packageLang': 'go',
            'license': 'PRIVATE',
            'status': 'OPEN',
            'policy': 'BC_LIC_1'
        }, {
            'packageName': 'github.com/davecgh/go-spew',
            'packageVersion': 'v1.1.1',
            'packageLang': 'go',
            'license': None,
            'status': 'COMPLIANT',
            'policy': 'BC_LIC_1'
        }]
    }


@pytest.fixture()
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
        },
        {
            "repository": "/path/to/go.sum",
            "passed": True,
            "packages": [
                {
                    "type": "go",
                    "name": "github.com/jstemmer/go-junit-report",
                    "version": "v0.0.0-20190106144839-af01ea7f8024",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/modern-go/reflect2",
                    "version": "v1.0.1",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/uber/jaeger-lib",
                    "version": "v2.0.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/kisielk/errcheck",
                    "version": "v1.5.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/gogo/protobuf",
                    "version": "v1.3.2",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/ghodss/yaml",
                    "version": "v1.0.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/NYTimes/gziphandler",
                    "version": "v0.0.0-20170623195520-56545f4a5d46",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "gopkg.in/fsnotify.v1",
                    "version": "v1.4.7",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/client9/misspell",
                    "version": "v0.3.4",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/Azure/go-autorest/autorest/date",
                    "version": "v0.1.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "golang.org/x/text",
                    "version": "v0.3.6",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/uber/jaeger-client-go",
                    "version": "v2.16.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/golang/protobuf",
                    "version": "v1.4.2",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/hashicorp/go-multierror",
                    "version": "v1.0.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "k8s.io/api",
                    "version": "v0.18.6",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/PuerkitoBio/purell",
                    "version": "v1.1.1",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/yuin/gopher-lua",
                    "version": "v0.0.0-20200603152657-dc2b0ca8b37e",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/PuerkitoBio/urlesc",
                    "version": "v0.0.0-20170810143723-de5bf2ad4578",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/julienschmidt/httprouter",
                    "version": "v1.2.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/coreos/go-oidc",
                    "version": "v2.0.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/spf13/afero",
                    "version": "v1.2.2",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/smartystreets/assertions",
                    "version": "v1.1.1",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/Azure/go-autorest/tracing",
                    "version": "v0.5.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "golang.org/x/tools",
                    "version": "v0.1.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "golang.org/x/mod",
                    "version": "v0.3.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "gopkg.in/alecthomas/kingpin.v2",
                    "version": "v2.2.6",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/fsnotify/fsnotify",
                    "version": "v1.4.9",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/kr/pretty",
                    "version": "v0.1.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/go-openapi/jsonpointer",
                    "version": "v0.19.3",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/hashicorp/go-uuid",
                    "version": "v1.0.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/opentracing/opentracing-go",
                    "version": "v1.1.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/hashicorp/memberlist",
                    "version": "v0.1.4",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/docker/spdystream",
                    "version": "v0.0.0-20160310174837-449fdfce4d96",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/go-kit/kit",
                    "version": "v0.8.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/miekg/dns",
                    "version": "v1.1.41",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "golang.org/x/crypto",
                    "version": "v0.0.0-20200622213623-75b288015ac9",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/onsi/gomega",
                    "version": "v1.10.3",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/uber-go/atomic",
                    "version": "v1.4.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "golang.org/x/mobile",
                    "version": "v0.0.0-20190312151609-d3739f865fa6",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "google.golang.org/protobuf",
                    "version": "v1.23.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/go-ole/go-ole",
                    "version": "v1.2.4",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/golang/groupcache",
                    "version": "v0.0.0-20190702054246-869f871628b6",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "golang.org/x/oauth2",
                    "version": "v0.0.0-20190604053449-0f29369cfe45",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "google.golang.org/api",
                    "version": "v0.4.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/yookoala/gofast",
                    "version": "v0.6.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/kr/logfmt",
                    "version": "v0.0.0-20140226030751-b84e30acd515",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/go-openapi/spec",
                    "version": "v0.19.3",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "gopkg.in/ini.v1",
                    "version": "v1.38.2",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/chzyer/test",
                    "version": "v0.0.0-20180213035817-a1ea475d72b1",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "golang.org/x/lint",
                    "version": "v0.0.0-20190313153728-d0100b6bd8b3",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/prometheus/common",
                    "version": "v0.4.1",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/pquerna/cachecontrol",
                    "version": "v0.0.0-20180517163645-1555304b9b35",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "modernc.org/cc",
                    "version": "v1.0.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "k8s.io/code-generator",
                    "version": "v0.17.6",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "google.golang.org/grpc",
                    "version": "v1.22.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "honnef.co/go/tools",
                    "version": "v0.0.0-20190523083050-ea95bdfd59fc",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "sigs.k8s.io/yaml",
                    "version": "v1.2.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/go-logr/logr",
                    "version": "v0.1.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/shirou/gopsutil",
                    "version": "v3.21.2",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/peterbourgon/diskv",
                    "version": "v2.0.1",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/yuin/goldmark",
                    "version": "v1.2.1",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "golang.org/x/image",
                    "version": "v0.0.0-20190227222117-0694c2d4d067",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/sarslanhan/cronmask",
                    "version": "v0.0.0-20190709075623-766eca24d011",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/armon/go-metrics",
                    "version": "v0.0.0-20180917152333-f0300d1749da",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "gopkg.in/tomb.v1",
                    "version": "v1.0.0-20141024135613-dd632973f1e7",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/cenkalti/backoff",
                    "version": "v2.2.1",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/googleapis/gnostic",
                    "version": "v0.1.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/StackExchange/wmi",
                    "version": "v0.0.0-20190523213315-cbe66965904d",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/sony/gobreaker",
                    "version": "v0.4.1",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "golang.org/x/term",
                    "version": "v0.0.0-20201126162022-7de9c90e9dd1",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "go.uber.org/atomic",
                    "version": "v1.4.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/spf13/pflag",
                    "version": "v1.0.5",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "sigs.k8s.io/structured-merge-diff/v3",
                    "version": "v3.0.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/mailru/easyjson",
                    "version": "v0.7.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "golang.org/x/exp",
                    "version": "v0.0.0-20190312203227-4b39c73a6495",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/pascaldekloe/goe",
                    "version": "v0.0.0-20180627143212-57f6aae5913c",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "layeh.com/gopher-json",
                    "version": "v0.0.0-20190114024228-97fed8db8427",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/golang/glog",
                    "version": "v0.0.0-20160126235308-23def4e6c14b",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "go.opentelemetry.io/otel",
                    "version": "v0.13.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/opentracing/basictracer-go",
                    "version": "v1.0.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "k8s.io/klog",
                    "version": "v1.0.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "golang.org/x/sys",
                    "version": "v0.0.0-20210415045647-66c3f260301c",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "modernc.org/mathutil",
                    "version": "v1.0.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/felixge/httpsnoop",
                    "version": "v1.0.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "sigs.k8s.io/structured-merge-diff/v2",
                    "version": "v2.0.1",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/emicklei/go-restful",
                    "version": "v2.9.5",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/instana/go-sensor",
                    "version": "v1.4.16",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/remyoudompheng/bigfft",
                    "version": "v0.0.0-20170806203942-52369c62f446",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/json-iterator/go",
                    "version": "v1.1.8",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/lightstep/lightstep-tracer-common/golang/gogo",
                    "version": "v0.0.0-20210210170715-a8dfcb80d3a7",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "gopkg.in/square/go-jose.v2",
                    "version": "v2.3.1",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/kisielk/gotool",
                    "version": "v1.0.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/google/uuid",
                    "version": "v1.1.1",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/stretchr/testify",
                    "version": "v1.6.1",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "cloud.google.com/go",
                    "version": "v0.38.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "modernc.org/xc",
                    "version": "v1.0.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/tidwall/match",
                    "version": "v1.0.3",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "golang.org/x/net",
                    "version": "v0.0.0-20210415231046-e915ea6b2b7d",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/google/go-cmp",
                    "version": "v0.5.2",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/chzyer/logex",
                    "version": "v1.1.10",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/chzyer/readline",
                    "version": "v0.0.0-20180603132655-2972be24d48e",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/hashicorp/errwrap",
                    "version": "v1.0.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/codahale/hdrhistogram",
                    "version": "v0.0.0-20161010025455-3a0bb77429bd",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "google.golang.org/appengine",
                    "version": "v1.5.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/tklauser/numcpus",
                    "version": "v0.2.2",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/aryszka/jobqueue",
                    "version": "v0.0.2",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/golang/mock",
                    "version": "v1.2.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/tklauser/go-sysconf",
                    "version": "v0.3.5",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/mxk/go-flowrate",
                    "version": "v0.0.0-20140419014527-cca7078d478f",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/looplab/fsm",
                    "version": "v0.1.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/tidwall/gjson",
                    "version": "v1.7.4",
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
                },
                {
                    "type": "go",
                    "name": "github.com/sanity-io/litter",
                    "version": "v1.1.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/kr/pty",
                    "version": "v1.1.5",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "k8s.io/gengo",
                    "version": "v0.0.0-20190822140433-26a664648505",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/oklog/ulid",
                    "version": "v1.3.1",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/munnerz/goautoneg",
                    "version": "v0.0.0-20120707110453-a547fc61f48d",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/hashicorp/go-sockaddr",
                    "version": "v1.0.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/hashicorp/go-immutable-radix",
                    "version": "v1.0.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "google.golang.org/genproto",
                    "version": "v0.0.0-20190530194941-fb225487d101",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/go-restit/lzjson",
                    "version": "v0.0.0-20161206095556-efe3c53acc68",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/hpcloud/tail",
                    "version": "v1.0.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/BurntSushi/xgb",
                    "version": "v0.0.0-20160522181843-27f122750802",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/Azure/go-autorest/autorest/mocks",
                    "version": "v0.2.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "k8s.io/client-go",
                    "version": "v0.17.6",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/beorn7/perks",
                    "version": "v1.0.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/nxadm/tail",
                    "version": "v1.4.4",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "gonum.org/v1/gonum",
                    "version": "v0.0.0-20190331200053-3d26580ed485",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/BurntSushi/toml",
                    "version": "v0.3.1",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/stretchr/objx",
                    "version": "v0.2.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/cespare/xxhash/v2",
                    "version": "v2.1.1",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "modernc.org/golex",
                    "version": "v1.0.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "k8s.io/kube-openapi",
                    "version": "v0.0.0-20200410145947-bcb3869e6f29",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/mwitkow/go-conntrack",
                    "version": "v0.0.0-20161129095857-cc309e4a2223",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "gonum.org/v1/netlib",
                    "version": "v0.0.0-20190331212654-76723241ea4e",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/google/btree",
                    "version": "v1.0.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/gophercloud/gophercloud",
                    "version": "v0.1.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/imdario/mergo",
                    "version": "v0.3.5",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "golang.org/x/sync",
                    "version": "v0.0.0-20210220032951-036812b2e83c",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/konsorten/go-windows-terminal-sequences",
                    "version": "v1.0.1",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/google/pprof",
                    "version": "v0.0.0-20181206194817-3ea8567a2e57",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "golang.org/x/xerrors",
                    "version": "v0.0.0-20200804184101-5ec99f83aff1",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/evanphx/json-patch",
                    "version": "v4.2.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/go-stack/stack",
                    "version": "v1.8.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/matttproud/golang_protobuf_extensions",
                    "version": "v1.0.1",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "gopkg.in/yaml.v2",
                    "version": "v2.4.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "gopkg.in/yaml.v3",
                    "version": "v3.0.0-20200313102051-9f266ea9e77c",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "gopkg.in/inf.v0",
                    "version": "v0.9.1",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "gopkg.in/check.v1",
                    "version": "v1.0.0-20180628173108-788fd7840127",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/prometheus/procfs",
                    "version": "v0.0.2",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/szuecs/rate-limit-buffer",
                    "version": "v0.7.1",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/go-redis/redis/v8",
                    "version": "v8.3.3",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/googleapis/gax-go/v2",
                    "version": "v2.0.4",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/go-openapi/swag",
                    "version": "v0.19.5",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/google/gofuzz",
                    "version": "v1.1.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/onsi/ginkgo",
                    "version": "v1.14.2",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/jtolds/gls",
                    "version": "v4.20.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/go-openapi/jsonreference",
                    "version": "v0.19.3",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/smartystreets/goconvey",
                    "version": "v1.6.4",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/alecthomas/units",
                    "version": "v0.0.0-20151022065526-2efee857e7cf",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "k8s.io/apimachinery",
                    "version": "v0.18.6",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/modern-go/concurrent",
                    "version": "v0.0.0-20180306012644-bacd9c7ef1dd",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/elazarl/goproxy",
                    "version": "v0.0.0-20180725130230-947c36da3153",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/gopherjs/gopherjs",
                    "version": "v0.0.0-20200217142428-fce0ec30dd00",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/pmezard/go-difflib",
                    "version": "v1.0.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/hashicorp/go-msgpack",
                    "version": "v0.5.3",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/prometheus/client_golang",
                    "version": "v1.0.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/alecthomas/template",
                    "version": "v0.0.0-20160405071501-a0175ee3bccc",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/cjoudrey/gluaurl",
                    "version": "v0.0.0-20161028222611-31cbb9bef199",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/tidwall/pretty",
                    "version": "v1.1.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/dgryski/go-rendezvous",
                    "version": "v0.0.0-20200823014737-9f7001d12a5f",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/sean-/seed",
                    "version": "v0.0.0-20170313163322-e2103e2c3529",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/lightstep/lightstep-tracer-go",
                    "version": "v0.24.1-0.20210318180546-a67254760a58",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "go.opencensus.io",
                    "version": "v0.22.3",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/Azure/go-autorest/logger",
                    "version": "v0.1.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/kr/text",
                    "version": "v0.1.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/google/martian",
                    "version": "v2.1.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/gregjones/httpcache",
                    "version": "v0.0.0-20180305231024-9cad4c3443a7",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "k8s.io/utils",
                    "version": "v0.0.0-20191114184206-e782cd3c129f",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/sirupsen/logrus",
                    "version": "v1.4.2",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/rcrowley/go-metrics",
                    "version": "v0.0.0-20181016184325-3113b8401b8a",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/go-logfmt/logfmt",
                    "version": "v0.3.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/davecgh/go-spew",
                    "version": "v1.1.1",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/Azure/go-autorest/autorest",
                    "version": "v0.9.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "golang.org/x/time",
                    "version": "v0.0.0-20190308202827-9d24e82272b4",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/hashicorp/golang-lru",
                    "version": "v0.5.1",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "modernc.org/strutil",
                    "version": "v1.0.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/cjoudrey/gluahttp",
                    "version": "v0.0.0-20190104103309-101c19a37344",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/Azure/go-autorest/autorest/adal",
                    "version": "v0.5.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/pkg/errors",
                    "version": "v0.8.1",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/szuecs/routegroup-client",
                    "version": "v0.17.7",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/abbot/go-http-auth",
                    "version": "v0.4.0",
                    "path": "/path/to/go.sum",
                },
                {
                    "type": "go",
                    "name": "github.com/dimfeld/httppath",
                    "version": "v0.0.0-20170720192232-ee938bf73598",
                    "path": "/path/to/go.sum",
                },
            ],
            "complianceIssues": None,
            "complianceDistribution": {"critical": 0, "high": 0, "medium": 0, "low": 0, "total": 0},
            "vulnerabilities": [
                {
                    "id": "CVE-2020-29652",
                    "status": "fixed in v0.0.0-20201216223049-8b5274cf687f",
                    "cvss": 7.5,
                    "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H",
                    "description": "A nil pointer dereference in the golang.org/x/crypto/ssh component through v0.0.0-20201203163018-be400aefbc4c for Go allows remote attackers to cause a denial of service against SSH servers.",
                    "severity": "high",
                    "packageName": "golang.org/x/crypto",
                    "packageVersion": "v0.0.0-20200622213623-75b288015ac9",
                    "link": "https://nvd.nist.gov/vuln/detail/CVE-2020-29652",
                    "riskFactors": [
                        "Has fix",
                        "High severity",
                        "Attack complexity: low",
                        "Attack vector: network",
                        "DoS",
                    ],
                    "impactedVersions": ["<v0.0.0-20201216223049-8b5274cf687f"],
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


@pytest.fixture()
def license_violation_result_success_response() -> Dict[str, Any]:
    return {
        "packages": [
            {
                "packageName": "github.com/armon/go-metrics",
                "packageVersion": "v0.0.0-20180917152333-f0300d1749da",
                "packageLang": "go",
                "license": "PRIVATE",
                "status": "OPEN",
                "policy": "BC_LIC_1"
            },
            {
                "packageName": "github.com/chzyer/readline",
                "packageVersion": "v0.0.0-20180603132655-2972be24d48e",
                "packageLang": "go",
                "license": "PRIVATE",
                "status": "OPEN",
                "policy": "BC_LIC_1"
            },
            {
                "packageName": "github.com/davecgh/go-spew",
                "packageVersion": "v1.1.1",
                "packageLang": "go",
                "license": None,
                "status": "COMPLIANT",
                "policy": "BC_LIC_1"
            }]
    }

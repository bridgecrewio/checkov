import os
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock
from typing import Dict, Any, List, Generator

import pytest
from pytest_mock import MockerFixture

from checkov.common.bridgecrew.bc_source import SourceType
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration, bc_integration
from checkov.common.output.report import Report
from checkov.sca_package_2.runner import Runner
from checkov.sca_package_2.output import create_cli_license_violations_table, create_cli_output
from checkov.runner_filter import RunnerFilter
from checkov.common.sca.commons import get_package_alias
from checkov.common.sca.output import create_report_cve_record, create_report_license_record

EXAMPLES_DIR = Path(__file__).parent / "examples"

@pytest.fixture(autouse=True)
def mock_env_vars():
    with mock.patch.dict(os.environ, {"CHECKOV_RUN_SCA_PACKAGE_SCAN_V2": "true"}):
        yield


@pytest.fixture()
def mock_bc_integration() -> BcPlatformIntegration:
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    bc_integration.api_url = 'https://www.bridgecrew.cloud'
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
        "/requirements.txt": {
            "repository": "/requirements.txt",
            "passed": True,
            "packages": [
                {
                    "type": "python",
                    "name": "requests",
                    "version": "2.26.0",
                    "path": "/requirements.txt",
                    "registry": "https://pypi.python.org/",
                },
                {
                    "type": "python",
                    "name": "django",
                    "version": "1.2",
                    "path": "/requirements.txt",
                    "registry": "https://pypi.python.org/"
                },
                {
                    "type": "python",
                    "name": "flask",
                    "version": "0.6",
                    "path": "/requirements.txt",
                    "registry": "https://pypi.python.org/"
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
                    'riskFactors': {'Critical severity': {}, 'Attack complexity: low': {}, 'Has fix': {}, 'Remote execution': {}, 'Attack vector: network': {}},
                    'riskFactorsV2': {'Severity': 'Critical', 'HasFix': True, 'DoS': False, 'AttackComplexity': 'low', 'AttackVector': 'network', 'RemoteExecution': True},
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
                    'riskFactors': {'Critical severity': {}, 'Attack complexity: low': {}, 'Has fix': {}, 'Remote execution': {}, 'Attack vector: network': {}},
                    'riskFactorsV2': {'Severity': 'Critical', 'HasFix': True, 'DoS': False, 'AttackComplexity': 'low', 'AttackVector': 'network', 'RemoteExecution': True},
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
                    'riskFactors': {'Critical severity': {}, 'Attack complexity: low': {}, 'Has fix': {}, 'Remote execution': {}, 'Attack vector: network': {}},
                    'riskFactorsV2': {'Severity': 'Critical', 'HasFix': True, 'DoS': False, 'AttackComplexity': 'low', 'AttackVector': 'network', 'RemoteExecution': True},
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
                    'riskFactors': {'Critical severity': {}, 'Attack complexity: low': {}, 'Has fix': {}, 'Remote execution': {}, 'Attack vector: network': {}},
                    'riskFactorsV2': {'Severity': 'Critical', 'HasFix': True, 'DoS': False, 'AttackComplexity': 'low', 'AttackVector': 'network', 'RemoteExecution': True},
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
                    'riskFactors': {'Critical severity': {}, 'Attack complexity: low': {}, 'Has fix': {}, 'Remote execution': {}, 'Attack vector: network': {}},
                    'riskFactorsV2': {'Severity': 'Critical', 'HasFix': True, 'DoS': False, 'AttackComplexity': 'low', 'AttackVector': 'network', 'RemoteExecution': True},
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
                    'riskFactors': {'Critical severity': {}, 'Attack complexity: low': {}, 'Has fix': {}, 'Remote execution': {}, 'Attack vector: network': {}},
                    'riskFactorsV2': {'Severity': 'Critical', 'HasFix': True, 'DoS': False, 'AttackComplexity': 'low', 'AttackVector': 'network', 'RemoteExecution': True},
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
            "inlineSuppressions": {
                "cves": {
                    "byCve": [
                        {
                            "cveId": "CVE-2019-1010083",
                            "reason": "Test CVE suppression 1"
                        },
                        {
                            "cveId": "CVE-2016-6186",
                            "reason": "Test CVE suppression 2"
                        }
                    ]
                },
                "licenses": {
                    "byPackage": [
                        {
                            "licenses": [],
                            "licensePolicy": "BC_LIC_1",
                            "packageName": "django",
                            "reason": "Test License suppression 1"
                        }
                    ]
                }
            }
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
                    'riskFactors': {'Critical severity': {}, 'Attack complexity: low': {}, 'Has fix': {}, 'Remote execution': {}, 'Attack vector: network': {}},
                    'riskFactorsV2': {'Severity': 'Critical', 'HasFix': True, 'DoS': False, 'AttackComplexity': 'low', 'AttackVector': 'network', 'RemoteExecution': True},
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
                    'riskFactors': {'Critical severity': {}, 'Attack complexity: low': {}, 'Has fix': {}, 'Remote execution': {}, 'Attack vector: network': {}},
                    'riskFactorsV2': {'Severity': 'Critical', 'HasFix': True, 'DoS': False, 'AttackComplexity': 'low', 'AttackVector': 'network', 'RemoteExecution': True},
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
def scan_results_dt() -> Dict[str, Dict[str, Any]]:
    return {
        '/empty/package-lock.json':
            {'branch': '', 'cicdDetails': {'runId': 1, 'pr': '', 'commit': '', 'scaCliScanId': '1670509263116'},
             'filePath': '/empty/package-lock.json', 'name': 'package-lock.json', 'packages': [],
             'sourceId': 'ajbara_cli_repo/ScaGoat-main', 'sourceType': 'CLI', 'type': 'Package', 'vulnerabilities': [],
             'dependencyTreeS3ObjectKey': 'dependency_tree/ajbara/ajbara_cli_repo/ScaGoat-main/1670509263116/src/empty/dependency-tree-package-lock.json',
             'email': '', 'customerName': 'ajbara', 'dependencies': {}, 'repositoryId': ''},
        '/package-files/java/maven/normal/pom.xml':
            {'sourceId': 'ajbara_cli_repo/ScaGoat-main', 'type': 'Package', 'branch': '', 'sourceType': 'CLI',
             'vulnerabilities': [
                 {'cveId': 'CVE-2020-15250', 'status': 'fixed in 4.13.1', 'severity': 'moderate',
                  'packageName': 'junit_junit', 'packageVersion': '4.12',
                  'link': 'https://nvd.nist.gov/vuln/detail/CVE-2020-15250', 'cvss': 4,
                  'vector': 'CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N',
                  'description': "In JUnit4 from version 4.7 and before 4.13.1, the test rule TemporaryFolder contains a local information disclosure vulnerability. On Unix like systems, the system\\'s temporary directory is shared between all users on that system. Because of this, when files and directories are written into this directory they are, by default, readable by other users on that same system. This vulnerability does not allow other users to overwrite the contents of these directories or files. This is purely an information disclosure vulnerability. This vulnerability impacts you if the JUnit tests write sensitive information, like API keys or passwords, into the temporary folder, and the JUnit tests execute in an environment where the OS has other untrusted users. Because certain JDK file system APIs were only added in JDK 1.7, this this fix is dependent upon the version of the JDK you are using. For Java 1.7 and higher users: this vulnerability is fixed in 4.13.1. For Java 1.6 and lower users: no patch is available, you must use the workaround below. If you are unable to patch, or are stuck running on Java 1.6, specifying the `java.io.tmpdir` system environment variable to a directory that is exclusively owned by the executing user will fix this vulnerability. For more information, including an example of vulnerable code, see the referenced GitHub Security Advisory.",
                  'riskFactors': {'Medium severity': {}, 'Attack complexity: low': {}, 'Has fix': {}},
                  'riskFactorsV2': {'Severity': 'Medium', 'HasFix': True, 'DoS': False, 'AttackComplexity': 'low'},
                  'publishedDate': '2020-10-12T17:33:00Z'},
                 {'cveId': 'CVE-2015-6420', 'status': 'fixed in 3.2.2', 'severity': 'high',
                  'packageName': 'commons-collections_commons-collections', 'packageVersion': '3.0',
                  'link': 'https://nvd.nist.gov/vuln/detail/CVE-2015-6420', 'cvss': 7,
                  'vector': 'AV:N/AC:L/Au:N/C:P/I:P/A:P',
                  'description': 'Serialized-object interfaces in certain Cisco Collaboration and Social Media; Endpoint Clients and Client Software; Network Application, Service, and Acceleration; Network and Content Security Devices; Network Management and Provisioning; Routing and Switching - Enterprise and Service Provider; Unified Computing; Voice and Unified Communications Devices; Video, Streaming, TelePresence, and Transcoding Devices; Wireless; and Cisco Hosted Services products allow remote attackers to execute arbitrary commands via a crafted serialized Java object, related to the Apache Commons Collections (ACC) library.',
                  'riskFactors': {'Critical severity': {}, 'Attack complexity: low': {}, 'Has fix': {}, 'Remote execution': {}, 'Attack vector: network': {}},
                  'riskFactorsV2': {'Severity': 'Critical', 'HasFix': True, 'DoS': False, 'AttackComplexity': 'low', 'AttackVector': 'network', 'RemoteExecution': True},
                  'publishedDate': '2020-06-15T20:36:20Z'},
                 {'cveId': 'CVE-2015-7501', 'status': 'fixed in 3.2.2', 'severity': 'critical',
                  'packageName': 'commons-collections_commons-collections', 'packageVersion': '3.0',
                  'link': 'https://nvd.nist.gov/vuln/detail/CVE-2015-7501', 'cvss': 9,
                  'vector': 'CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H',
                  'description': 'Red Hat JBoss A-MQ 6.x; BPM Suite (BPMS) 6.x; BRMS 6.x and 5.x; Data Grid (JDG) 6.x; Data Virtualization (JDV) 6.x and 5.x; Enterprise Application Platform 6.x, 5.x, and 4.3.x; Fuse 6.x; Fuse Service Works (FSW) 6.x; Operations Network (JBoss ON) 3.x; Portal 6.x; SOA Platform (SOA-P) 5.x; Web Server (JWS) 3.x; Red Hat OpenShift/xPAAS 3.x; and Red Hat Subscription Asset Manager 1.3 allow remote attackers to execute arbitrary commands via a crafted serialized Java object, related to the Apache Commons Collections (ACC) library.',
                  'riskFactors': {'Critical severity': {}, 'Attack complexity: low': {}, 'Has fix': {}, 'Remote execution': {}, 'Attack vector: network': {}},
                  'riskFactorsV2': {'Severity': 'Critical', 'HasFix': True, 'DoS': False, 'AttackComplexity': 'low', 'AttackVector': 'network', 'RemoteExecution': True},
                  'publishedDate': '2022-05-13T01:25:20Z'},
                 {'cveId': 'CVE-2021-45046', 'status': 'fixed in 2.16.0, 2.12.2, 2.3.1', 'severity': 'critical',
                  'packageName': 'org.apache.logging.log4j_log4j-core', 'packageVersion': '2.14.0',
                  'link': 'https://logging.apache.org/log4j/2.x/security.html#CVE-2021-45046', 'cvss': 9,
                  'vector': 'CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H',
                  'description': 'It was found that the fix to address CVE-2021-44228 in Apache Log4j 2.15.0 was incomplete in certain non-default configurations. This could allows attackers with control over Thread Context Map (MDC) input data when the logging configuration uses a non-default Pattern Layout with either a Context Lookup (for example, $${ctx:loginId}) or a Thread Context Map pattern (%X, %mdc, or %MDC) to craft malicious input data using a JNDI Lookup pattern resulting in an information leak and remote code execution in some environments and local code execution in all environments. Log4j 2.16.0 (Java 8) and 2.12.2 (Java 7) fix this issue by removing support for message lookup patterns and disabling JNDI functionality by default.',
                  'riskFactors': {'Critical severity': {}, 'Attack complexity: low': {}, 'Has fix': {}, 'Remote execution': {}, 'Attack vector: network': {}},
                  'riskFactorsV2': {'Severity': 'Critical', 'HasFix': True, 'DoS': False, 'AttackComplexity': 'low', 'AttackVector': 'network', 'RemoteExecution': True},
                  'publishedDate': '2021-12-14T19:15:00Z'},
                 {'cveId': 'CVE-2021-45105', 'status': 'fixed in 2.17.0, 2.12.3, 2.3.1', 'severity': 'high',
                  'packageName': 'org.apache.logging.log4j_log4j-core', 'packageVersion': '2.14.0',
                  'link': 'https://logging.apache.org/log4j/2.x/security.html#CVE-2021-45105', 'cvss': 7.5,
                  'vector': 'CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H',
                  'description': 'Apache Log4j2 versions 2.0-alpha1 through 2.16.0 (excluding 2.12.3 and 2.3.1) did not protect from uncontrolled recursion from self-referential lookups. This allows an attacker with control over Thread Context Map data to cause a denial of service when a crafted string is interpreted. This issue was fixed in Log4j 2.17.0, 2.12.3, and 2.3.1.',
                  'riskFactors': {'Critical severity': {}, 'Attack complexity: low': {}, 'Has fix': {}, 'Remote execution': {}, 'Attack vector: network': {}},
                  'riskFactorsV2': {'Severity': 'Critical', 'HasFix': True, 'DoS': False, 'AttackComplexity': 'low', 'AttackVector': 'network', 'RemoteExecution': True},
                  'publishedDate': '2021-12-18T18:00:07Z'},
                 {'cveId': 'CVE-2021-44832', 'status': 'fixed in 2.17.1, 2.12.4, 2.3.2', 'severity': 'medium',
                  'packageName': 'org.apache.logging.log4j_log4j-core', 'packageVersion': '2.14.0',
                  'link': 'https://logging.apache.org/log4j/2.x/security.html#CVE-2021-44832', 'cvss': 6.6,
                  'vector': 'CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H',
                  'description': 'Apache Log4j2 versions 2.0-beta7 through 2.17.0 (excluding security fix releases 2.3.2 and 2.12.4) are vulnerable to a remote code execution (RCE) attack when a configuration uses a JDBC Appender with a JNDI LDAP data source URI when an attacker has control of the target LDAP server. This issue is fixed by limiting JNDI data source names to the java protocol in Log4j2 versions 2.17.1, 2.12.4, and 2.3.2.',
                  'riskFactors': {'Critical severity': {}, 'Attack complexity: low': {}, 'Has fix': {}, 'Remote execution': {}, 'Attack vector: network': {}},
                  'riskFactorsV2': {'Severity': 'Critical', 'HasFix': True, 'DoS': False, 'AttackComplexity': 'low', 'AttackVector': 'network', 'RemoteExecution': True},
                  'publishedDate': '2021-12-28T20:15:00Z'},
                 {'cveId': 'CVE-2021-44228', 'status': 'fixed in 2.15.0, 2.12.2', 'severity': 'critical',
                  'packageName': 'org.apache.logging.log4j_log4j-core', 'packageVersion': '2.14.0',
                  'link': 'https://logging.apache.org/log4j/2.x/security.html#CVE-2021-44228', 'cvss': 10,
                  'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H',
                  'description': 'Apache Log4j2 2.0-beta9 through 2.15.0 (excluding security releases 2.12.2, 2.12.3, and 2.3.1) JNDI features used in configuration, log messages, and parameters do not protect against attacker controlled LDAP and other JNDI related endpoints. An attacker who can control log messages or log message parameters can execute arbitrary code loaded from LDAP servers when message lookup substitution is enabled. From log4j 2.15.0, this behavior has been disabled by default. From version 2.16.0 (along with 2.12.2, 2.12.3, and 2.3.1), this functionality has been completely removed. Note that this vulnerability is specific to log4j-core and does not affect log4net, log4cxx, or other Apache Logging Services projects.',
                  'riskFactors': {'Critical severity': {}, 'Attack complexity: low': {}, 'Has fix': {}, 'Remote execution': {}, 'Attack vector: network': {}},
                  'riskFactorsV2': {'Severity': 'Critical', 'HasFix': True, 'DoS': False, 'AttackComplexity': 'low', 'AttackVector': 'network', 'RemoteExecution': True},
                  'publishedDate': '2021-12-10T10:15:00Z'}],
             'name': 'pom.xml',
             'filePath': '/package-files/java/maven/normal/pom.xml',
             'fileContent': None, 'packages': [
                {'type': 'jar', 'name': 'junit_junit', 'version': '4.12', 'licenses': []},
                {'type': 'jar', 'name': 'commons-collections_commons-collections', 'version': '3.0',
                 'licenses': []},
                {'type': 'jar', 'name': 'org.apache.logging.log4j_log4j-core', 'version': '2.14.0',
                 'licenses': []}],
             'cicdDetails': {'runId': 1, 'pr': '', 'commit': '',
                             'scaCliScanId': '1670509263116'},
             'customerName': 'ajbara',
             'email': 'ajbara@paloaltonetworks.com',
             'license_statuses': []},
        '/package-files/yarn/package.json':
            {'sourceId': 'ajbara_cli_repo/ScaGoat-main', 'type': 'Package', 'branch': '', 'sourceType': 'CLI',
             'vulnerabilities': [
                 {'cveId': 'PRISMA-2021-0013', 'status': 'fixed in 1.1.1', 'severity': 'medium',
                  'packageName': 'marked',
                  'packageVersion': '0.3.9', 'link': None, 'cvss': None, 'vector': None,
                  'description': 'marked package prior to 1.1.1 are vulnerable to  Regular Expression Denial of Service (ReDoS). The regex within src/rules.js file have multiple unused capture groups which could lead to a denial of service attack if user input is reachable.  Origin: https://github.com/markedjs/marked/commit/bd4f8c464befad2b304d51e33e89e567326e62e0',
                  'riskFactors': {'Critical severity': {}, 'Attack complexity: low': {}, 'Has fix': {}, 'Remote execution': {}, 'Attack vector: network': {}},
                  'riskFactorsV2': {'Severity': 'Critical', 'HasFix': True, 'DoS': False, 'AttackComplexity': 'low', 'AttackVector': 'network', 'RemoteExecution': True},
                  'publishedDate': '2021-01-14T10:29:35Z'},
                 {'cveId': 'CVE-2022-21681', 'status': 'fixed in 4.0.10', 'severity': 'high',
                  'packageName': 'marked',
                  'packageVersion': '0.3.9', 'link': 'https://github.com/advisories/GHSA-5v2h-r2cx-5xgj',
                  'cvss': 7.5,
                  'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H',
                  'description': 'Marked is a markdown parser and compiler. Prior to version 4.0.10, the regular expression `inline.reflinkSearch` may cause catastrophic backtracking against some strings and lead to a denial of service (DoS). Anyone who runs untrusted markdown through a vulnerable version of marked and does not use a worker with a time limit may be affected. This issue is patched in version 4.0.10. As a workaround, avoid running untrusted markdown through marked or run marked on a worker thread and set a reasonable time limit to prevent draining resources.',
                  'riskFactors': {'Critical severity': {}, 'Attack complexity: low': {}, 'Has fix': {}, 'Remote execution': {}, 'Attack vector: network': {}},
                  'riskFactorsV2': {'Severity': 'Critical', 'HasFix': True, 'DoS': False, 'AttackComplexity': 'low', 'AttackVector': 'network', 'RemoteExecution': True},
                  'publishedDate': '2022-01-14T17:15:00Z'},
                 {'cveId': 'CVE-2022-21680', 'status': 'fixed in 4.0.10', 'severity': 'high',
                  'packageName': 'marked',
                  'packageVersion': '0.3.9', 'link': 'https://github.com/advisories/GHSA-rrrm-qjm4-v8hf',
                  'cvss': 7.5,
                  'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H',
                  'description': 'Marked is a markdown parser and compiler. Prior to version 4.0.10, the regular expression `block.def` may cause catastrophic backtracking against some strings and lead to a regular expression denial of service (ReDoS). Anyone who runs untrusted markdown through a vulnerable version of marked and does not use a worker with a time limit may be affected. This issue is patched in version 4.0.10. As a workaround, avoid running untrusted markdown through marked or run marked on a worker thread and set a reasonable time limit to prevent draining resources.',
                  'riskFactors': {'Critical severity': {}, 'Attack complexity: low': {}, 'Has fix': {}, 'Remote execution': {}, 'Attack vector: network': {}},
                  'riskFactorsV2': {'Severity': 'Critical', 'HasFix': True, 'DoS': False, 'AttackComplexity': 'low', 'AttackVector': 'network', 'RemoteExecution': True},
                  'publishedDate': '2022-01-14T17:15:00Z'}],
             'name': 'package.json', 'filePath': '/package-files/yarn/package.json',
             'fileContent': None, 'packages': [
                {'type': 'nodejs', 'name': 'marked', 'version': '0.3.9', 'licenses': []},
                {'type': 'nodejs', 'name': 'csurf', 'version': '', 'licenses': []},
                {'type': 'nodejs', 'name': 'cypress', 'version': '', 'licenses': []},
                {'type': 'nodejs', 'name': 'mongodb', 'version': '', 'licenses': []},
                {'type': 'nodejs', 'name': 'grunt-cli', 'version': '', 'licenses': []},
                {'type': 'nodejs', 'name': 'zaproxy', 'version': '', 'licenses': []},
                {'type': 'nodejs', 'name': 'should', 'version': '', 'licenses': []},
                {'type': 'nodejs', 'name': 'nodemon', 'version': '', 'licenses': []},
                {'type': 'nodejs', 'name': 'underscore', 'version': '', 'licenses': []},
                {'type': 'nodejs', 'name': 'serve-favicon', 'version': '', 'licenses': []},
                {'type': 'nodejs', 'name': 'swig', 'version': '', 'licenses': []}],
             'cicdDetails': {'runId': 1, 'pr': '', 'commit': '',
                             'scaCliScanId': '1670509263116'},
             'customerName': 'ajbara',
             'email': 'ajbara@paloaltonetworks.com', 'license_statuses': [
                {'packageName': 'bcrypt-nodejs', 'packageVersion': '0.0.3', 'packageLang': 'nodejs',
                 'license': 'NOT_FOUND', 'status': 'OPEN', 'policy': 'BC_LIC_2'},
                {'packageName': 'marked', 'packageVersion': '0.3.9', 'packageLang': 'nodejs', 'license': 'MIT',
                 'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                {'packageName': 'needle', 'packageVersion': '2.2.4', 'packageLang': 'nodejs', 'license': 'MIT',
                 'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                {'packageName': 'node-esapi', 'packageVersion': '0.0.1', 'packageLang': 'nodejs',
                 'license': 'NOT_FOUND',
                 'status': 'OPEN', 'policy': 'BC_LIC_2'}]},
        '/package-lock.json':
            {'branch': '', 'cicdDetails': {'runId': 1, 'pr': '', 'commit': '', 'scaCliScanId': '1670509263116'}, 'filePath': '/package-lock.json', 'name': 'package-lock.json', 'packages': [{'name': '@cypress/listr-verbose-renderer', 'version': '0.4.1', 'root': False}, {'name': 'chalk', 'version': '1.1.3', 'root': False}, {'name': 'supports-color', 'version': '2.0.0', 'root': False}, {'name': '@cypress/xvfb', 'version': '1.2.4',    'root': False}, {'name': 'debug', 'version': '3.2.7',   'root': False}, {'name': 'ms','version': '2.1.3', 'root': False}, {'name': '@types/sizzle','version': '2.3.2', 'root': False}, {'name': 'abbrev', 'version': '1.1.1', 'root': False},  {'name': 'accepts', 'version': '1.3.8', 'root': False}, {'name': 'mime-types', 'version': '2.1.34',  'root': False}, {'name': 'negotiator','version': '0.6.3','root': False},  {'name': 'adm-zip', 'version': '0.4.4', 'root': False,'cves_index': [3, 4]}, {'name': 'ajv', 'version': '6.12.6',  'root': False}, {'name': 'amdefine',      'version': '1.0.1', 'root': False}, {'name': 'ansi-align', 'version': '2.0.0', 'root': False}, {'name': 'ansi-regex',  'version': '3.0.0',  'root': False,  'cves_index': [0]}, {  'name': 'is-fullwidth-code-point',   'version': '2.0.0',    'root': False},{'name': 'string-width','version': '2.1.1','root': False},   {'name': 'strip-ansi', 'version': '4.0.0', 'root': False}, {'name': 'ansi-escapes', 'version': '1.4.0', 'root': False}, {'name': 'ansi-regex', 'version': '2.1.1', 'root': False}, {'name': 'ansi-styles', 'version': '2.2.1', 'root': False}, {'name': 'anymatch', 'version': '2.0.0', 'root': False}, {'name': 'micromatch', 'version': '3.1.10', 'root': False}, {'name': 'normalize-path', 'version': '2.1.1', 'root': False}, {'name': 'remove-trailing-separator', 'version': '1.1.0', 'root': False}, {'name': 'arch', 'version': '2.1.1', 'root': False}, {'name': 'argparse', 'version': '1.0.10', 'root': False}, {'name': 'sprintf-js', 'version': '1.0.3', 'root': False}, {'name': 'arr-diff', 'version': '4.0.0', 'root': False}, {'name': 'arr-flatten', 'version': '1.1.0', 'root': False}, {'name': 'arr-union', 'version': '3.1.0', 'root': False}, {'name': 'array-each', 'version': '1.0.1', 'root': False}, {'name': 'array-find-index', 'version': '1.0.2', 'root': False}, {'name': 'array-flatten', 'version': '1.1.1', 'root': False}, {'name': 'array-slice', 'version': '1.1.0', 'root': False}, {'name': 'array-unique', 'version': '0.3.2', 'root': False}, {'name': 'arrify', 'version': '1.0.1', 'root': False}, {'name': 'asap', 'version': '2.0.6', 'root': False}, {'name': 'asn1', 'version': '0.2.6', 'root': False}, {'name': 'assert-plus', 'version': '1.0.0', 'root': False}, {'name': 'assign-symbols', 'version': '1.0.0', 'root': False}, {'name': 'async', 'version': '2.6.3', 'root': False, 'cves_index': [2]}, {'name': 'async-each', 'version': '1.0.3', 'root': False}, {'name': 'asynckit', 'version': '0.4.0', 'root': False}, {'name': 'atob', 'version': '2.1.2', 'root': False}, {'name': 'available-typed-arrays', 'version': '1.0.5', 'root': False}, {'name': 'aws-sign2', 'version': '0.7.0', 'root': False}, {'name': 'aws4', 'version': '1.11.0', 'root': False}, {'name': 'balanced-match', 'version': '1.0.2', 'root': False}, {'name': 'base', 'version': '0.11.2', 'root': False}, {'name': 'cache-base', 'version': '1.0.1', 'root': False}, {'name': 'class-utils', 'version': '0.3.6', 'root': False}, {'name': 'component-emitter', 'version': '1.3.0', 'root': False}, {'name': 'define-property', 'version': '1.0.0', 'root': False}, {'name': 'isobject', 'version': '3.0.1', 'root': False}, {'name': 'mixin-deep', 'version': '1.3.2', 'root': False}, {'name': 'pascalcase', 'version': '0.1.1', 'root': False}, {'name': 'is-descriptor', 'version': '1.0.2', 'root': False}, {'name': 'is-accessor-descriptor', 'version': '1.0.0', 'root': False}, {'name': 'is-data-descriptor', 'version': '1.0.0', 'root': False}, {'name': 'kind-of', 'version': '6.0.3', 'root': False}, {'name': 'bcrypt-nodejs', 'version': '0.0.3', 'root': True}, {'name': 'bcrypt-pbkdf', 'version': '1.0.2', 'root': False}, {'name': 'binary-extensions', 'version': '1.13.1', 'root': False}, {'name': 'bindings', 'version': '1.5.0', 'root': False}, {'name': 'file-uri-to-path', 'version': '1.0.0', 'root': False}, {'name': 'bl', 'version': '1.0.3', 'root': False, 'cves_index': [1]}, {'name': 'isarray', 'version': '1.0.0', 'root': False}, {'name': 'process-nextick-args', 'version': '1.0.7', 'root': False}, {'name': 'readable-stream', 'version': '2.0.6', 'root': False}, {'name': 'string_decoder', 'version': '0.10.31', 'root': False}, {'name': 'bluebird', 'version': '3.7.2', 'root': False}, {'name': 'body', 'version': '5.1.0', 'root': False}, {'name': 'bytes', 'version': '1.0.0', 'root': False}, {'name': 'raw-body', 'version': '1.1.7', 'root': False}, {'name': 'body-parser', 'version': '1.19.2', 'root': False}, {'name': 'bytes', 'version': '3.1.2', 'root': False}, {'name': 'content-type', 'version': '1.0.4', 'root': False}, {'name': 'debug', 'version': '2.6.9', 'root': False}, {'name': 'depd', 'version': '1.1.2', 'root': False}, {'name': 'http-errors', 'version': '1.8.1', 'root': False}, {'name': 'iconv-lite', 'version': '0.4.24', 'root': False}, {'name': 'on-finished', 'version': '2.3.0', 'root': False}, {'name': 'qs', 'version': '6.9.7', 'root': False}, {'name': 'raw-body', 'version': '2.4.3', 'root': False}, {'name': 'type-is', 'version': '1.6.18', 'root': False}, {'name': 'boom', 'version': '2.10.1', 'root': False}, {'name': 'boxen', 'version': '1.3.0', 'root': False}, {'name': 'camelcase', 'version': '4.1.0', 'root': False}, {'name': 'brace-expansion', 'version': '1.1.11', 'root': False}, {'name': 'concat-map', 'version': '0.0.1', 'root': False}, {'name': 'braces', 'version': '2.3.2', 'root': False}, {'name': 'extend-shallow', 'version': '2.0.1', 'root': False}, {'name': 'fill-range', 'version': '4.0.0', 'root': False}, {'name': 'repeat-element', 'version': '1.1.4', 'root': False}, {'name': 'snapdragon', 'version': '0.8.2', 'root': False}, {'name': 'snapdragon-node', 'version': '2.1.1', 'root': False}, {'name': 'split-string', 'version': '3.1.0', 'root': False}, {'name': 'to-regex', 'version': '3.0.2', 'root': False}, {'name': 'is-extendable', 'version': '0.1.1', 'root': False}, {'name': 'broadway', 'version': '0.3.6', 'root': False}, {'name': 'cliff', 'version': '0.1.9', 'root': False}, {'name': 'eventemitter2', 'version': '0.4.14', 'root': False}, {'name': 'nconf', 'version': '0.6.9', 'root': False, 'cves_index': [5]}, {'name': 'utile', 'version': '0.2.1', 'root': False}, {'name': 'winston', 'version': '0.8.0', 'root': False}, {'name': 'async', 'version': '0.2.10', 'root': False}, {'name': 'async', 'version': '0.2.9', 'root': False}, {'name': 'optimist', 'version': '0.6.0', 'root': False}, {'name': 'colors', 'version': '0.6.2', 'root': False}, {'name': 'eyes', 'version': '0.1.8', 'root': False}, {'name': 'ini', 'version': '1.3.8', 'root': False}, {'name': 'minimist', 'version': '0.0.10', 'root': False, 'cves_index': [11, 12]}, {'name': 'wordwrap', 'version': '0.0.3', 'root': False}, {'name': 'deep-equal', 'version': '2.0.5', 'root': False}, {'name': 'i', 'version': '0.3.7', 'root': False}, {'name': 'mkdirp', 'version': '0.5.5', 'root': False}, {'name': 'ncp', 'version': '0.4.2', 'root': False}, {'name': 'rimraf', 'version': '2.7.1', 'root': False}, {'name': 'cycle', 'version': '1.0.3', 'root': False}, {'name': 'pkginfo', 'version': '0.3.1', 'root': False}, {'name': 'stack-trace', 'version': '0.0.10', 'root': False}, {'name': 'bson', 'version': '1.0.9', 'root': False, 'cves_index': [6, 7]}, {'name': 'buffer-crc32', 'version': '0.2.13', 'root': False}, {'name': 'buffer-from', 'version': '1.1.2', 'root': False}, {'name': 'buffer-shims', 'version': '1.0.0', 'root': False}, {'name': 'collection-visit', 'version': '1.0.0', 'root': False}, {'name': 'get-value', 'version': '2.0.6', 'root': False}, {'name': 'has-value', 'version': '1.0.0', 'root': False}, {'name': 'set-value', 'version': '2.0.1', 'root': False}, {'name': 'to-object-path', 'version': '0.3.0', 'root': False}, {'name': 'union-value', 'version': '1.0.1', 'root': False}, {'name': 'unset-value', 'version': '1.0.0', 'root': False, 'cves_index': [9]}, {'name': 'cachedir', 'version': '1.3.0', 'root': False}, {'name': 'call-bind', 'version': '1.0.2', 'root': False}, {'name': 'function-bind', 'version': '1.1.1', 'root': False}, {'name': 'get-intrinsic', 'version': '1.1.1', 'root': False}, {'name': 'caller', 'version': '0.0.1', 'root': False}, {'name': 'tape', 'version': '2.3.3', 'root': False}, {'name': 'camelcase', 'version': '2.1.1', 'root': False}, {'name': 'camelcase-keys', 'version': '2.1.0', 'root': False}, {'name': 'camelize', 'version': '1.0.0', 'root': False}, {'name': 'capture-stack-trace', 'version': '1.0.1', 'root': False}, {'name': 'caseless', 'version': '0.12.0', 'root': False}, {'name': 'chalk', 'version': '2.4.2', 'root': False}, {'name': 'ansi-styles', 'version': '3.2.1', 'root': False}, {'name': 'check-more-types', 'version': '2.24.0', 'root': False}, {'name': 'chokidar', 'version': '2.1.8', 'root': False}, {'name': 'fsevents', 'version': '1.2.13', 'root': False}, {'name': 'glob-parent', 'version': '3.1.0', 'root': False, 'cves_index': [10]}, {'name': 'inherits', 'version': '2.0.4', 'root': False}, {'name': 'is-binary-path', 'version': '1.0.1', 'root': False}, {'name': 'is-glob', 'version': '4.0.3', 'root': False}, {'name': 'normalize-path', 'version': '3.0.0', 'root': False}, {'name': 'path-is-absolute', 'version': '1.0.1', 'root': False}, {'name': 'readdirp', 'version': '2.2.1', 'root': False}, {'name': 'upath', 'version': '1.2.0', 'root': False}, {'name': 'ci-info', 'version': '1.6.0', 'root': False}, {'name': 'define-property', 'version': '0.2.5', 'root': False}, {'name': 'static-extend', 'version': '0.1.2', 'root': False}, {'name': 'is-descriptor', 'version': '0.1.6', 'root': False}, {'name': 'clean-yaml-object', 'version': '0.1.0', 'root': False}, {'name': 'cli', 'version': '1.0.1', 'root': False}, {'name': 'cli-boxes', 'version': '1.0.0', 'root': False}, {'name': 'cli-cursor', 'version': '1.0.2', 'root': False}, {'name': 'cli-spinners', 'version': '0.1.2', 'root': False}, {'name': 'cli-truncate', 'version': '0.2.1', 'root': False}, {'name': 'cliff', 'version': '0.1.10', 'root': False}, {'name': 'colors', 'version': '1.0.3', 'root': False}, {'name': 'winston', 'version': '0.8.3', 'root': False}, {'name': 'cliui', 'version': '3.2.0', 'root': False}, {'name': 'string-width', 'version': '1.0.2', 'root': False}, {'name': 'strip-ansi', 'version': '3.0.1', 'root': False}, {'name': 'wrap-ansi', 'version': '2.1.0', 'root': False}, {'name': 'clone', 'version': '2.1.2', 'root': False}, {'name': 'code-point-at', 'version': '1.1.0', 'root': False}, {'name': 'map-visit', 'version': '1.0.0', 'root': False}, {'name': 'object-visit', 'version': '1.0.1', 'root': False}, {'name': 'color-convert', 'version': '1.9.3', 'root': False}, {'name': 'color-name', 'version': '1.1.3', 'root': False}, {'name': 'color-support', 'version': '1.1.3', 'root': False}, {'name': 'combined-stream', 'version': '1.0.8', 'root': False}, {'name': 'commander', 'version': '2.15.1', 'root': False}, {'name': 'common-tags', 'version': '1.8.0', 'root': False}, {'name': 'concat-stream', 'version': '1.6.2', 'root': False}, {'name': 'config-chain', 'version': '1.1.13', 'root': False}, {'name': 'configstore', 'version': '3.1.5', 'root': False}, {'name': 'connect', 'version': '3.4.1', 'root': False}, {'name': 'debug', 'version': '2.2.0', 'root': False, 'cves_index': [8]}, {'name': 'finalhandler', 'version': '0.4.1', 'root': False}, {'name': 'parseurl', 'version': '1.3.3', 'root': False}, {'name': 'utils-merge', 'version': '1.0.0', 'root': False}, {'name': 'ms', 'version': '0.7.1', 'root': False}, {'name': 'escape-html', 'version': '1.0.3', 'root': False}, {'name': 'unpipe', 'version': '1.0.0', 'root': False}, {'name': 'console-browserify', 'version': '1.1.0', 'root': False}, {'name': 'consolidate', 'version': '0.14.5', 'root': True}, {'name': 'content-disposition', 'version': '0.5.4', 'root': False}, {'name': 'safe-buffer', 'version': '5.2.1', 'root': False}, {'name': 'content-security-policy-builder', 'version': '1.0.0', 'root': False}, {'name': 'dashify', 'version': '0.2.2', 'root': False}, {'name': 'continuable-cache', 'version': '0.3.1', 'root': False}, {'name': 'cookie', 'version': '0.4.0', 'root': False}, {'name': 'cookie-signature', 'version': '1.0.6', 'root': False}, {'name': 'copy-descriptor', 'version': '0.1.1', 'root': False}, {'name': 'core-util-is', 'version': '1.0.3', 'root': False}, {'name': 'coveralls', 'version': '2.13.3', 'root': False}, {'name': 'assert-plus', 'version': '0.2.0', 'root': False}, {'name': 'aws-sign2', 'version': '0.6.0', 'root': False}, {'name': 'caseless', 'version': '0.11.0', 'root': False}, {'name': 'esprima', 'version': '2.7.3', 'root': False}, {'name': 'form-data', 'version': '2.1.4', 'root': False}, {'name': 'har-validator', 'version': '2.0.6', 'root': False}, {'name': 'http-signature', 'version': '1.1.1', 'root': False}, {'name': 'js-yaml', 'version': '3.6.1', 'root': False, 'cves_index': [16, 15]}, {'name': 'minimist', 'version': '1.2.0', 'root': False, 'cves_index': [22, 23]}, {'name': 'oauth-sign', 'version': '0.8.2', 'root': False}, {'name': 'punycode', 'version': '1.4.1', 'root': False}, {'name': 'qs', 'version': '6.3.3', 'root': False}, {'name': 'request', 'version': '2.79.0', 'root': False}, {'name': 'tough-cookie', 'version': '2.3.4', 'root': False}, {'name': 'tunnel-agent', 'version': '0.4.3', 'root': False, 'cves_index': [18]}, {'name': 'create-error-class', 'version': '3.0.2', 'root': False}, {'name': 'cross-env', 'version': '7.0.3', 'root': True}, {'name': 'cross-spawn', 'version': '7.0.3', 'root': False}, {'name': 'cryptiles', 'version': '2.0.5', 'root': False, 'cves_index': [14]}, {'name': 'crypto-random-string', 'version': '1.0.0', 'root': False}, {'name': 'csrf', 'version': '3.1.0', 'root': False}, {'name': 'rndm', 'version': '1.2.0', 'root': False}, {'name': 'tsscmp', 'version': '1.0.6', 'root': False}, {'name': 'uid-safe', 'version': '2.1.5', 'root': False}, {'name': 'csurf', 'version': '1.11.0', 'root': True}, {'name': 'http-errors', 'version': '1.7.3', 'root': False}, {'name': 'setprototypeof', 'version': '1.1.1', 'root': False}, {'name': 'toidentifier', 'version': '1.0.0', 'root': False}, {'name': 'statuses', 'version': '1.5.0', 'root': False}, {'name': 'ctype', 'version': '0.5.3', 'root': False}, {'name': 'currently-unhandled', 'version': '0.4.1', 'root': False}, {'name': 'cypress', 'version': '3.8.3', 'root': True, 'cves_index': [17]}, {'name': 'bluebird', 'version': '3.5.0', 'root': False}, {'name': 'debug', 'version': '3.2.6', 'root': False}, {'name': 'eventemitter2', 'version': '4.1.2', 'root': False}, {'name': 'lodash', 'version': '4.17.15', 'root': False, 'cves_index': [19, 20, 21]}, {'name': 'dashdash', 'version': '1.14.1', 'root': False}, {'name': 'date-fns', 'version': '1.30.1', 'root': False}, {'name': 'date-now', 'version': '0.1.4', 'root': False}, {'name': 'dateformat', 'version': '3.0.3', 'root': False}, {'name': 'ms', 'version': '2.0.0', 'root': False}, {'name': 'debuglog', 'version': '1.0.1', 'root': False}, {'name': 'decamelize', 'version': '1.2.0', 'root': False}, {'name': 'decode-uri-component', 'version': '0.2.0', 'root': False, 'cves_index': [13]}, {'name': 'es-get-iterator', 'version': '1.1.2', 'root': False}, {'name': 'is-arguments', 'version': '1.1.1', 'root': False}, {'name': 'is-date-object', 'version': '1.0.5', 'root': False}, {'name': 'is-regex', 'version': '1.1.4', 'root': False}, {'name': 'isarray', 'version': '2.0.5', 'root': False}, {'name': 'object-is', 'version': '1.1.5', 'root': False}, {'name': 'object-keys', 'version': '1.1.1', 'root': False}, {'name': 'object.assign', 'version': '4.1.2', 'root': False}, {'name': 'regexp.prototype.flags', 'version': '1.4.1', 'root': False}, {'name': 'side-channel', 'version': '1.0.4', 'root': False}, {'name': 'which-boxed-primitive', 'version': '1.0.2', 'root': False}, {'name': 'which-collection', 'version': '1.0.1', 'root': False}, {'name': 'which-typed-array', 'version': '1.1.7', 'root': False}, {'name': 'deep-extend', 'version': '0.6.0', 'root': False}, {'name': 'deeper', 'version': '2.1.0', 'root': False}, {'name': 'define-properties', 'version': '1.1.3', 'root': False}, {'name': 'define-property', 'version': '2.0.2', 'root': False}, {'name': 'defined', 'version': '0.0.0', 'root': False}, {'name': 'delayed-stream', 'version': '1.0.0', 'root': False}, {'name': 'destroy', 'version': '1.0.4', 'root': False}, {'name': 'detect-file', 'version': '1.0.0', 'root': False}, {'name': 'dezalgo', 'version': '1.0.3', 'root': False}, {'name': 'diff', 'version': '1.4.0', 'root': False, 'cves_index': [24]}, {'name': 'director', 'version': '1.2.7', 'root': False}, {'name': 'dns-prefetch-control', 'version': '0.1.0', 'root': False}, {'name': 'dom-serializer', 'version': '0.2.2', 'root': False}, {'name': 'domelementtype', 'version': '2.2.0', 'root': False}, {'name': 'entities', 'version': '2.2.0', 'root': False}, {'name': 'domelementtype', 'version': '1.3.1', 'root': False}, {'name': 'domhandler', 'version': '2.3.0', 'root': False}, {'name': 'domutils', 'version': '1.5.1', 'root': False}, {'name': 'dont-sniff-mimetype', 'version': '1.1.0', 'root': True}, {'name': 'dot-prop', 'version': '4.2.1', 'root': False}, {'name': 'duplexer3', 'version': '0.1.4', 'root': False}, {'name': 'duplexify', 'version': '3.7.1', 'root': False}, {'name': 'ecc-jsbn', 'version': '0.1.2', 'root': False}, {'name': 'editorconfig', 'version': '0.15.3', 'root': False}, {'name': 'commander', 'version': '2.20.3', 'root': False}, {'name': 'ee-first', 'version': '1.1.1', 'root': False}, {'name': 'elegant-spinner', 'version': '1.0.1', 'root': False}, {'name': 'encodeurl', 'version': '1.0.2', 'root': False}, {'name': 'end-of-stream', 'version': '1.4.4', 'root': False}, {'name': 'entities', 'version': '1.0.0', 'root': False}, {'name': 'error', 'version': '7.2.1', 'root': False}, {'name': 'error-ex', 'version': '1.3.2', 'root': False}, {'name': 'es-abstract', 'version': '1.19.1', 'root': False}, {'name': 'es-to-primitive', 'version': '1.2.1', 'root': False}, {'name': 'get-symbol-description', 'version': '1.0.0', 'root': False}, {'name': 'has', 'version': '1.0.3', 'root': False}, {'name': 'has-symbols', 'version': '1.0.2', 'root': False}, {'name': 'internal-slot', 'version': '1.0.3', 'root': False}, {'name': 'is-callable', 'version': '1.2.4', 'root': False}, {'name': 'is-negative-zero', 'version': '2.0.2', 'root': False}, {'name': 'is-shared-array-buffer', 'version': '1.0.1', 'root': False}, {'name': 'is-string', 'version': '1.0.7', 'root': False}, {'name': 'is-weakref', 'version': '1.0.2', 'root': False}, {'name': 'object-inspect', 'version': '1.12.0', 'root': False}, {'name': 'string.prototype.trimend', 'version': '1.0.4', 'root': False}, {'name': 'string.prototype.trimstart', 'version': '1.0.4', 'root': False}, {'name': 'unbox-primitive', 'version': '1.0.1', 'root': False}, {'name': 'is-map', 'version': '2.0.2', 'root': False}, {'name': 'is-set', 'version': '2.0.2', 'root': False}, {'name': 'is-symbol', 'version': '1.0.4', 'root': False}, {'name': 'es6-promise', 'version': '3.2.1', 'root': False}, {'name': 'escape-string-regexp', 'version': '1.0.5', 'root': False}, {'name': 'esprima', 'version': '4.0.1', 'root': False}, {'name': 'etag', 'version': '1.8.1', 'root': False}, {'name': 'event-stream', 'version': '0.5.3', 'root': False}, {'name': 'optimist', 'version': '0.2.8', 'root': False}, {'name': 'events-to-array', 'version': '1.1.2', 'root': False}, {'name': 'execa', 'version': '0.10.0', 'root': False}, {'name': 'cross-spawn', 'version': '6.0.5', 'root': False}, {'name': 'path-key', 'version': '2.0.1', 'root': False}, {'name': 'shebang-command', 'version': '1.2.0', 'root': False}, {'name': 'shebang-regex', 'version': '1.0.0', 'root': False}, {'name': 'which', 'version': '1.3.1', 'root': False}, {'name': 'executable', 'version': '4.1.1', 'root': False}, {'name': 'exit', 'version': '0.1.2', 'root': False}, {'name': 'exit-hook', 'version': '1.1.1', 'root': False}, {'name': 'expand-brackets', 'version': '2.1.4', 'root': False}, {'name': 'posix-character-classes', 'version': '0.1.1', 'root': False}, {'name': 'regex-not', 'version': '1.0.2', 'root': False}, {'name': 'expand-tilde', 'version': '2.0.2', 'root': False}, {'name': 'express', 'version': '4.17.3', 'root': True}, {'name': 'cookie', 'version': '0.4.2', 'root': False}, {'name': 'finalhandler', 'version': '1.1.2', 'root': False}, {'name': 'fresh', 'version': '0.5.2', 'root': False}, {'name': 'merge-descriptors', 'version': '1.0.1', 'root': False}, {'name': 'methods', 'version': '1.1.2', 'root': False}, {'name': 'path-to-regexp', 'version': '0.1.7', 'root': False}, {'name': 'proxy-addr', 'version': '2.0.7', 'root': False}, {'name': 'range-parser', 'version': '1.2.1', 'root': False}, {'name': 'send', 'version': '0.17.2', 'root': False}, {'name': 'serve-static', 'version': '1.14.2', 'root': False}, {'name': 'setprototypeof', 'version': '1.2.0', 'root': False}, {'name': 'utils-merge', 'version': '1.0.1', 'root': False}, {'name': 'vary', 'version': '1.1.2', 'root': False}, {'name': 'express-session', 'version': '1.17.2', 'root': True}, {'name': 'cookie', 'version': '0.4.1', 'root': False}, {'name': 'depd', 'version': '2.0.0', 'root': False}, {'name': 'on-headers', 'version': '1.0.2', 'root': False}, {'name': 'extend', 'version': '3.0.2', 'root': False}, {'name': 'extend-shallow', 'version': '3.0.2', 'root': False}, {'name': 'is-extendable', 'version': '1.0.1', 'root': False}, {'name': 'is-plain-object', 'version': '2.0.4', 'root': False}, {'name': 'extglob', 'version': '2.0.4', 'root': False}, {'name': 'fragment-cache', 'version': '0.2.1', 'root': False}, {'name': 'extract-zip', 'version': '1.6.7', 'root': False}, {'name': 'minimist', 'version': '0.0.8', 'root': False, 'cves_index': [26, 27]}, {'name': 'mkdirp', 'version': '0.5.1', 'root': False}, {'name': 'yauzl', 'version': '2.4.1', 'root': False}, {'name': 'extsprintf', 'version': '1.3.0', 'root': False}, {'name': 'fast-deep-equal', 'version': '3.1.3', 'root': False}, {'name': 'fast-json-stable-stringify', 'version': '2.1.0', 'root': False}, {'name': 'faye-websocket', 'version': '0.10.0', 'root': False}, {'name': 'fd-slicer', 'version': '1.0.1', 'root': False}, {'name': 'figures', 'version': '1.7.0', 'root': False}, {'name': 'is-number', 'version': '3.0.0', 'root': False}, {'name': 'repeat-string', 'version': '1.6.1', 'root': False}, {'name': 'to-regex-range', 'version': '2.1.1', 'root': False}, {'name': 'find-up', 'version': '1.1.2', 'root': False}, {'name': 'findup-sync', 'version': '0.3.0', 'root': False}, {'name': 'glob', 'version': '5.0.15', 'root': False}, {'name': 'fined', 'version': '1.2.0', 'root': False}, {'name': 'flagged-respawn', 'version': '1.0.1', 'root': False}, {'name': 'flatiron', 'version': '0.4.3', 'root': False}, {'name': 'prompt', 'version': '0.2.14', 'root': False}, {'name': 'for-in', 'version': '1.0.2', 'root': False}, {'name': 'for-own', 'version': '1.0.0', 'root': False}, {'name': 'foreach', 'version': '2.0.5', 'root': False}, {'name': 'foreground-child', 'version': '1.5.6', 'root': False}, {'name': 'cross-spawn', 'version': '4.0.2', 'root': False}, {'name': 'forever', 'version': '2.0.0', 'root': True, 'vulnerable_dependencies': [387, 133, 104, 591, 113, 150, 251]}, {'name': 'async', 'version': '1.5.2', 'root': False}, {'name': 'forever-monitor', 'version': '2.0.0', 'root': False}, {'name': 'nconf', 'version': '0.10.0', 'root': False, 'cves_index': [25]}, {'name': 'nssocket', 'version': '0.6.0', 'root': False}, {'name': 'object-assign', 'version': '4.1.1', 'root': False}, {'name': 'optimist', 'version': '0.6.1', 'root': False}, {'name': 'path-is-absolute', 'version': '2.0.0', 'root': False}, {'name': 'prettyjson', 'version': '1.2.5', 'root': False}, {'name': 'shush', 'version': '1.0.0', 'root': False}, {'name': 'utile', 'version': '0.3.0', 'root': False}, {'name': 'forever-agent', 'version': '0.6.1', 'root': False}, {'name': 'minimatch', 'version': '3.1.2', 'root': False}, {'name': 'ps-tree', 'version': '0.0.3', 'root': False}, {'name': 'form-data', 'version': '2.3.3', 'root': False}, {'name': 'forwarded', 'version': '0.2.0', 'root': False}, {'name': 'map-cache', 'version': '0.2.2', 'root': False}, {'name': 'frameguard', 'version': '2.0.0', 'root': False}, {'name': 'fs-extra', 'version': '5.0.0', 'root': False}, {'name': 'fs.realpath', 'version': '1.0.0', 'root': False}, {'name': 'nan', 'version': '2.15.0', 'root': False}, {'name': 'gaze', 'version': '1.1.3', 'root': False}, {'name': 'generate-function', 'version': '2.3.1', 'root': False}, {'name': 'generate-object-property', 'version': '1.2.0', 'root': False}, {'name': 'get-stdin', 'version': '4.0.1', 'root': False}, {'name': 'get-stream', 'version': '3.0.0', 'root': False}, {'name': 'getobject', 'version': '1.0.2', 'root': False}, {'name': 'getos', 'version': '3.1.1', 'root': False}, {'name': 'async', 'version': '2.6.1', 'root': False, 'cves_index': [37]}, {'name': 'getpass', 'version': '0.1.7', 'root': False}, {'name': 'glob', 'version': '7.2.0', 'root': False}, {'name': 'inflight', 'version': '1.0.6', 'root': False}, {'name': 'once', 'version': '1.4.0', 'root': False}, {'name': 'is-glob', 'version': '3.1.0', 'root': False}, {'name': 'path-dirname', 'version': '1.0.2', 'root': False}, {'name': 'is-extglob', 'version': '2.1.1', 'root': False}, {'name': 'global-dirs', 'version': '0.1.1', 'root': False}, {'name': 'global-modules', 'version': '1.0.0', 'root': False}, {'name': 'global-prefix', 'version': '1.0.2', 'root': False}, {'name': 'globule', 'version': '1.3.3', 'root': False}, {'name': 'glob', 'version': '7.1.7', 'root': False}, {'name': 'minimatch', 'version': '3.0.8', 'root': False}, {'name': 'got', 'version': '6.7.1', 'root': False, 'cves_index': [39]}, {'name': 'graceful-fs', 'version': '4.2.9', 'root': False}, {'name': 'growl', 'version': '1.9.2', 'root': False, 'cves_index': [42]}, {'name': 'grunt', 'version': '1.4.1', 'root': True, 'cves_index': [32, 33]}, {'name': 'mkdirp', 'version': '1.0.4', 'root': False}, {'name': 'rimraf', 'version': '3.0.2', 'root': False}, {'name': 'grunt-cli', 'version': '1.4.3', 'root': True}, {'name': 'nopt', 'version': '4.0.3', 'root': False}, {'name': 'grunt-concurrent', 'version': '2.3.1', 'root': True}, {'name': 'grunt-contrib-clean', 'version': '1.1.0', 'root': False}, {'name': 'grunt-contrib-jshint', 'version': '1.1.0', 'root': True}, {'name': 'grunt-contrib-nodeunit', 'version': '1.0.0', 'root': False}, {'name': 'grunt-contrib-watch', 'version': '1.1.0', 'root': True}, {'name': 'grunt-env', 'version': '1.0.1', 'root': True}, {'name': 'grunt-if', 'version': 'https://github.com/binarymist/grunt-if/tarball/master', 'root': True}, {'name': 'grunt-jsbeautifier', 'version': '0.2.13', 'root': True}, {'name': 'grunt-known-options', 'version': '2.0.0', 'root': False}, {'name': 'grunt-legacy-log', 'version': '3.0.0', 'root': False}, {'name': 'colors', 'version': '1.1.2', 'root': False}, {'name': 'grunt-legacy-log-utils', 'version': '2.1.0', 'root': False}, {'name': 'ansi-styles', 'version': '4.3.0', 'root': False}, {'name': 'chalk', 'version': '4.1.2', 'root': False}, {'name': 'color-convert', 'version': '2.0.1', 'root': False}, {'name': 'color-name', 'version': '1.1.4', 'root': False}, {'name': 'has-flag', 'version': '4.0.0', 'root': False}, {'name': 'supports-color', 'version': '7.2.0', 'root': False}, {'name': 'grunt-legacy-util', 'version': '2.0.1', 'root': False}, {'name': 'async', 'version': '3.2.3', 'root': False}, {'name': 'grunt-mocha-test', 'version': '0.12.7', 'root': True}, {'name': 'grunt-npm-install', 'version': '0.3.1', 'root': True}, {'name': 'grunt-retire', 'version': '0.3.12', 'root': True}, {'name': 'form-data', 'version': '1.0.1', 'root': False}, {'name': 'node-uuid', 'version': '1.4.8', 'root': False}, {'name': 'qs', 'version': '5.2.1', 'root': False, 'cves_index': [29, 30, 31]}, {'name': 'request', 'version': '2.67.0', 'root': False, 'cves_index': [28]}, {'name': 'tough-cookie', 'version': '2.2.2', 'root': False, 'cves_index': [40, 41]}, {'name': 'har-schema', 'version': '2.0.0', 'root': False}, {'name': 'har-validator', 'version': '5.1.5', 'root': False}, {'name': 'has-ansi', 'version': '2.0.0', 'root': False}, {'name': 'has-bigints', 'version': '1.0.1', 'root': False}, {'name': 'has-flag', 'version': '3.0.0', 'root': False}, {'name': 'has-tostringtag', 'version': '1.0.0', 'root': False}, {'name': 'has-values', 'version': '1.0.0', 'root': False}, {'name': 'kind-of', 'version': '4.0.0', 'root': False}, {'name': 'is-buffer', 'version': '1.1.6', 'root': False}, {'name': 'hawk', 'version': '3.1.3', 'root': False, 'cves_index': [38]}, {'name': 'helmet', 'version': '2.3.0', 'root': True, 'vulnerable_dependencies': [474, 189], 'cves_index': [145, 142]}, {'name': 'dont-sniff-mimetype', 'version': '1.0.0', 'root': False}, {'name': 'helmet-csp', 'version': '1.2.2', 'root': False, 'cves_index': [36]}, {'name': 'hide-powered-by', 'version': '1.0.0', 'root': False}, {'name': 'hpkp', 'version': '1.2.0', 'root': False}, {'name': 'hsts', 'version': '1.0.0', 'root': False}, {'name': 'ienoopen', 'version': '1.0.0', 'root': False}, {'name': 'nocache', 'version': '1.0.1', 'root': False}, {'name': 'referrer-policy', 'version': '1.0.0', 'root': False}, {'name': 'x-xss-protection', 'version': '1.0.0', 'root': False}, {'name': 'lodash.reduce', 'version': '4.5.0', 'root': False}, {'name': 'platform', 'version': '1.3.1', 'root': False}, {'name': 'hoek', 'version': '2.16.3', 'root': False, 'cves_index': [34, 35]}, {'name': 'homedir-polyfill', 'version': '1.0.3', 'root': False}, {'name': 'hooker', 'version': '0.2.3', 'root': False}, {'name': 'hosted-git-info', 'version': '2.8.9', 'root': False}, {'name': 'core-util-is', 'version': '1.0.2', 'root': False}, {'name': 'htmlparser2', 'version': '3.8.3', 'root': False}, {'name': 'isarray', 'version': '0.0.1', 'root': False}, {'name': 'readable-stream', 'version': '1.1.14', 'root': False}, {'name': 'toidentifier', 'version': '1.0.1', 'root': False}, {'name': 'http-parser-js', 'version': '0.5.5', 'root': False}, {'name': 'http-signature', 'version': '1.2.0', 'root': False}, {'name': 'safer-buffer', 'version': '2.1.2', 'root': False}, {'name': 'ignore-by-default', 'version': '1.0.1', 'root': False}, {'name': 'import-lazy', 'version': '2.1.0', 'root': False}, {'name': 'imurmurhash', 'version': '0.1.4', 'root': False}, {'name': 'indent-string', 'version': '2.1.0', 'root': False}, {'name': 'wrappy', 'version': '1.0.2', 'root': False}, {'name': 'interpret', 'version': '1.1.0', 'root': False}, {'name': 'invert-kv', 'version': '1.0.0', 'root': False}, {'name': 'ipaddr.js', 'version': '1.9.1', 'root': False}, {'name': 'is-absolute', 'version': '1.0.0', 'root': False}, {'name': 'is-accessor-descriptor', 'version': '0.1.6', 'root': False}, {'name': 'kind-of', 'version': '3.2.2', 'root': False}, {'name': 'is-arrayish', 'version': '0.2.1', 'root': False}, {'name': 'is-bigint', 'version': '1.0.4', 'root': False}, {'name': 'is-boolean-object', 'version': '1.1.2', 'root': False}, {'name': 'is-ci', 'version': '1.2.1', 'root': False}, {'name': 'is-core-module', 'version': '2.8.1', 'root': False}, {'name': 'is-data-descriptor', 'version': '0.1.4', 'root': False}, {'name': 'kind-of', 'version': '5.1.0', 'root': False}, {'name': 'is-finite', 'version': '1.1.0', 'root': False}, {'name': 'is-fullwidth-code-point', 'version': '1.0.0', 'root': False}, {'name': 'number-is-nan', 'version': '1.0.1', 'root': False}, {'name': 'is-installed-globally', 'version': '0.1.0', 'root': False}, {'name': 'is-my-ip-valid', 'version': '1.0.0', 'root': False}, {'name': 'is-my-json-valid', 'version': '2.20.6', 'root': False}, {'name': 'is-npm', 'version': '1.0.0', 'root': False}, {'name': 'is-number-object', 'version': '1.0.6', 'root': False}, {'name': 'is-obj', 'version': '1.0.1', 'root': False}, {'name': 'is-path-inside', 'version': '1.0.1', 'root': False}, {'name': 'is-promise', 'version': '2.2.2', 'root': False}, {'name': 'is-property', 'version': '1.0.2', 'root': False}, {'name': 'is-redirect', 'version': '1.0.0', 'root': False}, {'name': 'is-relative', 'version': '1.0.0', 'root': False}, {'name': 'is-retry-allowed', 'version': '1.2.0', 'root': False}, {'name': 'is-stream', 'version': '1.1.0', 'root': False}, {'name': 'is-typed-array', 'version': '1.1.8', 'root': False}, {'name': 'is-typedarray', 'version': '1.0.0', 'root': False}, {'name': 'is-unc-path', 'version': '1.0.0', 'root': False}, {'name': 'is-utf8', 'version': '0.2.1', 'root': False}, {'name': 'is-weakmap', 'version': '2.0.1', 'root': False}, {'name': 'is-weakset', 'version': '2.0.2', 'root': False}, {'name': 'is-windows', 'version': '1.0.2', 'root': False}, {'name': 'isexe', 'version': '2.0.0', 'root': False}, {'name': 'isstream', 'version': '0.1.2', 'root': False}, {'name': 'jade', 'version': '0.26.3', 'root': False}, {'name': 'commander', 'version': '0.6.1', 'root': False}, {'name': 'mkdirp', 'version': '0.3.0', 'root': False}, {'name': 'js-beautify', 'version': '1.14.0', 'root': False}, {'name': 'nopt', 'version': '5.0.0', 'root': False}, {'name': 'js-yaml', 'version': '3.14.1', 'root': False}, {'name': 'jsbn', 'version': '0.1.1', 'root': False}, {'name': 'jshint', 'version': '2.9.7', 'root': False}, {'name': 'strip-json-comments', 'version': '1.0.4', 'root': False}, {'name': 'json-parse-even-better-errors', 'version': '2.3.1', 'root': False}, {'name': 'json-schema', 'version': '0.4.0', 'root': False}, {'name': 'json-schema-traverse', 'version': '0.4.1', 'root': False}, {'name': 'json-stringify-safe', 'version': '5.0.1', 'root': False}, {'name': 'jsonfile', 'version': '4.0.0', 'root': False}, {'name': 'jsonify', 'version': '0.0.0', 'root': False}, {'name': 'jsonpointer', 'version': '5.0.0', 'root': False}, {'name': 'jsprim', 'version': '1.4.2', 'root': False}, {'name': 'latest-version', 'version': '3.1.0', 'root': False}, {'name': 'lazy', 'version': '1.0.11', 'root': False}, {'name': 'lazy-ass', 'version': '1.6.0', 'root': False}, {'name': 'lcid', 'version': '1.0.0', 'root': False}, {'name': 'lcov-parse', 'version': '0.0.10', 'root': False}, {'name': 'liftup', 'version': '3.0.1', 'root': False}, {'name': 'braces', 'version': '3.0.2', 'root': False}, {'name': 'fill-range', 'version': '7.0.1', 'root': False}, {'name': 'findup-sync', 'version': '4.0.0', 'root': False}, {'name': 'is-number', 'version': '7.0.0', 'root': False}, {'name': 'micromatch', 'version': '4.0.4', 'root': False}, {'name': 'to-regex-range', 'version': '5.0.1', 'root': False}, {'name': 'listr', 'version': '0.12.0', 'root': False}, {'name': 'log-symbols', 'version': '1.0.2', 'root': False}, {'name': 'listr-silent-renderer', 'version': '1.1.1', 'root': False}, {'name': 'listr-update-renderer', 'version': '0.2.0', 'root': False}, {'name': 'indent-string', 'version': '3.2.0', 'root': False}, {'name': 'listr-verbose-renderer', 'version': '0.4.1', 'root': False}, {'name': 'livereload-js', 'version': '2.4.0', 'root': False}, {'name': 'load-json-file', 'version': '1.1.0', 'root': False}, {'name': 'lodash', 'version': '4.17.21', 'root': False}, {'name': 'lodash.once', 'version': '4.1.1', 'root': False}, {'name': 'log-driver', 'version': '1.2.5', 'root': False}, {'name': 'log-symbols', 'version': '2.2.0', 'root': False}, {'name': 'log-update', 'version': '1.0.2', 'root': False}, {'name': 'loud-rejection', 'version': '1.6.0', 'root': False}, {'name': 'lowercase-keys', 'version': '1.0.1', 'root': False}, {'name': 'lru-cache', 'version': '4.1.5', 'root': False}, {'name': 'make-dir', 'version': '1.3.0', 'root': False}, {'name': 'pify', 'version': '3.0.0', 'root': False}, {'name': 'make-iterator', 'version': '1.0.1', 'root': False}, {'name': 'map-obj', 'version': '1.0.1', 'root': False}, {'name': 'marked', 'version': '0.3.9', 'root': True, 'cves_index': [43, 44, 45]}, {'name': 'media-typer', 'version': '0.3.0', 'root': False}, {'name': 'meow', 'version': '3.7.0', 'root': False}, {'name': 'minimist', 'version': '1.2.5', 'root': False, 'cves_index': [46]}, {'name': 'nanomatch', 'version': '1.2.13', 'root': False}, {'name': 'object.pick', 'version': '1.3.0', 'root': False}, {'name': 'mime', 'version': '1.6.0', 'root': False}, {'name': 'mime-db', 'version': '1.51.0', 'root': False}, {'name': 'mocha', 'version': '2.5.3', 'root': True, 'cves_index': [48, 47]}, {'name': 'commander', 'version': '2.3.0', 'root': False}, {'name': 'escape-string-regexp', 'version': '1.0.2', 'root': False}, {'name': 'glob', 'version': '3.2.11', 'root': False}, {'name': 'lru-cache', 'version': '2.7.3', 'root': False}, {'name': 'minimatch', 'version': '0.3.0', 'root': False, 'cves_index': [57, 58, 59]}, {'name': 'supports-color', 'version': '1.2.0', 'root': False}, {'name': 'moment', 'version': '2.24.0', 'root': False, 'cves_index': [65, 66]}, {'name': 'mongodb', 'version': '2.2.36', 'root': True, 'cves_index': [143, 144, 55], 'vulnerable_dependencies': [123]}, {'name': 'mongodb-core', 'version': '2.1.20', 'root': False}, {'name': 'readable-stream', 'version': '2.2.7', 'root': False}, {'name': 'string_decoder', 'version': '1.0.3', 'root': False}, {'name': 'safe-buffer', 'version': '5.1.2', 'root': False}, {'name': 'util-deprecate', 'version': '1.0.2', 'root': False}, {'name': 'require_optional', 'version': '1.0.1', 'root': False}, {'name': 'mute-stream', 'version': '0.0.8', 'root': False}, {'name': 'secure-keys', 'version': '1.0.0', 'root': False}, {'name': 'yargs', 'version': '3.32.0', 'root': False}, {'name': 'needle', 'version': '2.2.4', 'root': True}, {'name': 'sax', 'version': '1.2.4', 'root': False}, {'name': 'nice-try', 'version': '1.0.5', 'root': False}, {'name': 'depd', 'version': '1.1.0', 'root': False}, {'name': 'node-esapi', 'version': '0.0.1', 'root': True}, {'name': 'nodemon', 'version': '1.19.4', 'root': True}, {'name': 'nodeunit', 'version': '0.9.5', 'root': False}, {'name': 'nopt', 'version': '3.0.6', 'root': False}, {'name': 'normalize-package-data', 'version': '2.5.0', 'root': False}, {'name': 'npm', 'version': '3.10.10', 'root': False, 'cves_index': [50, 51, 52, 53, 54]}, {'name': 'abbrev', 'version': '1.0.9', 'root': False}, {'name': 'ansi-regex', 'version': '2.0.0', 'root': False}, {'name': 'ansicolors', 'version': '0.3.2', 'root': False}, {'name': 'ansistyles', 'version': '0.1.3', 'root': False}, {'name': 'aproba', 'version': '1.0.4', 'root': False}, {'name': 'archy', 'version': '1.0.0', 'root': False}, {'name': 'asap', 'version': '2.0.5', 'root': False}, {'name': 'chownr', 'version': '1.0.1', 'root': False, 'cves_index': [63]}, {'name': 'cmd-shim', 'version': '2.0.2', 'root': False}, {'name': 'columnify', 'version': '1.5.4', 'root': False}, {'name': 'wcwidth', 'version': '1.0.0', 'root': False}, {'name': 'defaults', 'version': '1.0.3', 'root': False}, {'name': 'clone', 'version': '1.0.2', 'root': False}, {'name': 'config-chain', 'version': '1.1.11', 'root': False}, {'name': 'proto-list', 'version': '1.2.4', 'root': False}, {'name': 'editor', 'version': '1.0.0', 'root': False}, {'name': 'fs-vacuum', 'version': '1.2.9', 'root': False}, {'name': 'fs-write-stream-atomic', 'version': '1.0.8', 'root': False}, {'name': 'fstream', 'version': '1.0.10', 'root': False, 'cves_index': [64]}, {'name': 'fstream-npm', 'version': '1.2.0', 'root': False}, {'name': 'fstream-ignore', 'version': '1.0.5', 'root': False}, {'name': 'minimatch', 'version': '3.0.3', 'root': False, 'cves_index': [61, 62]}, {'name': 'brace-expansion', 'version': '1.1.6', 'root': False, 'cves_index': [60]}, {'name': 'balanced-match', 'version': '0.4.2', 'root': False}, {'name': 'glob', 'version': '7.1.0', 'root': False}, {'name': 'graceful-fs', 'version': '4.1.9', 'root': False}, {'name': 'has-unicode', 'version': '2.0.1', 'root': False}, {'name': 'hosted-git-info', 'version': '2.1.5', 'root': False, 'cves_index': [49]}, {'name': 'iferr', 'version': '0.1.5', 'root': False}, {'name': 'inflight', 'version': '1.0.5', 'root': False}, {'name': 'inherits', 'version': '2.0.3', 'root': False}, {'name': 'ini', 'version': '1.3.4', 'root': False, 'cves_index': [56]}, {'name': 'init-package-json', 'version': '1.9.4', 'root': False}, {'name': 'glob', 'version': '6.0.4', 'root': False}, {'name': 'path-is-absolute', 'version': '1.0.0', 'root': False}, {'name': 'promzard', 'version': '0.3.0', 'root': False}, {'name': 'lockfile', 'version': '1.0.2', 'root': False}, {'name': 'lodash._baseindexof', 'version': '3.1.0', 'root': False}, {'name': 'lodash._baseuniq', 'version': '4.6.0', 'root': False}, {'name': 'lodash._createset', 'version': '4.0.3', 'root': False}, {'name': 'lodash._root', 'version': '3.0.1', 'root': False}, {'name': 'lodash._bindcallback', 'version': '3.0.1', 'root': False}, {'name': 'lodash._cacheindexof', 'version': '3.0.2', 'root': False}, {'name': 'lodash._createcache', 'version': '3.1.2', 'root': False}, {'name': 'lodash._getnative', 'version': '3.9.1', 'root': False}, {'name': 'lodash.clonedeep', 'version': '4.5.0', 'root': False}, {'name': 'lodash.restparam', 'version': '3.6.1', 'root': False}, {'name': 'lodash.union', 'version': '4.6.0', 'root': False}, {'name': 'lodash.uniq', 'version': '4.5.0', 'root': False}, {'name': 'lodash.without', 'version': '4.4.0', 'root': False}, {'name': 'node-gyp', 'version': '3.4.0', 'root': False}, {'name': 'npmlog', 'version': '3.1.2', 'root': False}, {'name': 'are-we-there-yet', 'version': '1.1.2', 'root': False}, {'name': 'delegates', 'version': '1.0.0', 'root': False}, {'name': 'console-control-strings', 'version': '1.1.0', 'root': False}, {'name': 'gauge', 'version': '2.6.0', 'root': False}, {'name': 'has-color', 'version': '0.1.7', 'root': False}, {'name': 'object-assign', 'version': '4.1.0', 'root': False}, {'name': 'signal-exit', 'version': '3.0.0', 'root': False}, {'name': 'code-point-at', 'version': '1.0.0', 'root': False}, {'name': 'number-is-nan', 'version': '1.0.0', 'root': False}, {'name': 'wide-align', 'version': '1.1.0', 'root': False}, {'name': 'set-blocking', 'version': '2.0.0', 'root': False}, {'name': 'path-array', 'version': '1.0.1', 'root': False}, {'name': 'array-index', 'version': '1.0.0', 'root': False}, {'name': 'es6-symbol', 'version': '3.1.0', 'root': False}, {'name': 'd', 'version': '0.1.1', 'root': False}, {'name': 'es5-ext', 'version': '0.10.12', 'root': False}, {'name': 'es6-iterator', 'version': '2.0.0', 'root': False}, {'name': 'normalize-git-url', 'version': '3.0.2', 'root': False}, {'name': 'normalize-package-data', 'version': '2.3.5', 'root': False}, {'name': 'is-builtin-module', 'version': '1.0.0', 'root': False}, {'name': 'builtin-modules', 'version': '1.1.1', 'root': False}, {'name': 'npm-cache-filename', 'version': '1.0.2', 'root': False}, {'name': 'npm-install-checks', 'version': '3.0.0', 'root': False}, {'name': 'npm-package-arg', 'version': '4.2.0', 'root': False}, {'name': 'npm-registry-client', 'version': '7.2.1', 'root': False}, {'name': 'concat-stream', 'version': '1.5.2', 'root': False}, {'name': 'typedarray', 'version': '0.0.6', 'root': False}, {'name': 'retry', 'version': '0.10.0', 'root': False}, {'name': 'npm-user-validate', 'version': '0.1.5', 'root': False, 'cves_index': [74, 75]}, {'name': 'npmlog', 'version': '4.0.0', 'root': False}, {'name': 'opener', 'version': '1.4.2', 'root': False}, {'name': 'osenv', 'version': '0.1.3', 'root': False}, {'name': 'os-homedir', 'version': '1.0.1', 'root': False}, {'name': 'os-tmpdir', 'version': '1.0.1', 'root': False}, {'name': 'path-is-inside', 'version': '1.0.2', 'root': False}, {'name': 'read', 'version': '1.0.7', 'root': False}, {'name': 'mute-stream', 'version': '0.0.5', 'root': False}, {'name': 'read-cmd-shim', 'version': '1.0.1', 'root': False}, {'name': 'read-installed', 'version': '4.0.3', 'root': False}, {'name': 'util-extend', 'version': '1.0.3', 'root': False}, {'name': 'read-package-json', 'version': '2.0.4', 'root': False}, {'name': 'json-parse-helpfulerror', 'version': '1.0.3', 'root': False}, {'name': 'jju', 'version': '1.3.0', 'root': False}, {'name': 'read-package-tree', 'version': '5.1.5', 'root': False}, {'name': 'readable-stream', 'version': '2.1.5', 'root': False}, {'name': 'readdir-scoped-modules', 'version': '1.0.2', 'root': False}, {'name': 'realize-package-specifier', 'version': '3.0.3', 'root': False}, {'name': 'request', 'version': '2.75.0', 'root': False}, {'name': 'aws4', 'version': '1.4.1', 'root': False}, {'name': 'bl', 'version': '1.1.2', 'root': False, 'cves_index': [72]}, {'name': 'combined-stream', 'version': '1.0.5', 'root': False}, {'name': 'extend', 'version': '3.0.0', 'root': False, 'cves_index': [88]}, {'name': 'form-data', 'version': '2.0.0', 'root': False}, {'name': 'commander', 'version': '2.9.0', 'root': False}, {'name': 'graceful-readlink', 'version': '1.0.1', 'root': False}, {'name': 'is-my-json-valid', 'version': '2.15.0', 'root': False, 'cves_index': [70, 71]}, {'name': 'generate-function', 'version': '2.0.0', 'root': False}, {'name': 'jsonpointer', 'version': '4.0.0', 'root': False, 'cves_index': [86]}, {'name': 'xtend', 'version': '4.0.1', 'root': False}, {'name': 'pinkie-promise', 'version': '2.0.1', 'root': False}, {'name': 'pinkie', 'version': '2.0.4', 'root': False}, {'name': 'sntp', 'version': '1.0.9', 'root': False}, {'name': 'jsprim', 'version': '1.3.1', 'root': False}, {'name': 'extsprintf', 'version': '1.0.2', 'root': False}, {'name': 'json-schema', 'version': '0.2.3', 'root': False, 'cves_index': [85]}, {'name': 'verror', 'version': '1.3.6', 'root': False}, {'name': 'sshpk', 'version': '1.10.1', 'root': False}, {'name': 'asn1', 'version': '0.2.3', 'root': False}, {'name': 'bcrypt-pbkdf', 'version': '1.0.0', 'root': False}, {'name': 'dashdash', 'version': '1.14.0', 'root': False}, {'name': 'ecc-jsbn', 'version': '0.1.1', 'root': False}, {'name': 'getpass', 'version': '0.1.6', 'root': False}, {'name': 'jodid25519', 'version': '1.0.2', 'root': False}, {'name': 'jsbn', 'version': '0.1.0', 'root': False}, {'name': 'tweetnacl', 'version': '0.14.3', 'root': False}, {'name': 'mime-types', 'version': '2.1.12', 'root': False}, {'name': 'mime-db', 'version': '1.24.0', 'root': False}, {'name': 'node-uuid', 'version': '1.4.7', 'root': False}, {'name': 'qs', 'version': '6.2.1', 'root': False, 'cves_index': [67, 68, 69]}, {'name': 'stringstream', 'version': '0.0.5', 'root': False, 'cves_index': [73]}, {'name': 'tough-cookie', 'version': '2.3.1', 'root': False, 'cves_index': [87]}, {'name': 'rimraf', 'version': '2.5.4', 'root': False}, {'name': 'semver', 'version': '5.3.0', 'root': False}, {'name': 'sha', 'version': '2.0.1', 'root': False}, {'name': 'slide', 'version': '1.1.6', 'root': False}, {'name': 'sorted-object', 'version': '2.0.1', 'root': False}, {'name': 'tar', 'version': '2.2.1', 'root': False, 'cves_index': [78, 79, 80, 81, 82, 83, 84]}, {'name': 'block-stream', 'version': '0.0.8', 'root': False}, {'name': 'text-table', 'version': '0.2.0', 'root': False}, {'name': 'uid-number', 'version': '0.0.6', 'root': False}, {'name': 'umask', 'version': '1.1.0', 'root': False}, {'name': 'unique-filename', 'version': '1.1.0', 'root': False}, {'name': 'unique-slug', 'version': '2.0.0', 'root': False}, {'name': 'validate-npm-package-license', 'version': '3.0.1', 'root': False}, {'name': 'spdx-correct', 'version': '1.0.2', 'root': False}, {'name': 'spdx-license-ids', 'version': '1.2.0', 'root': False}, {'name': 'spdx-expression-parse', 'version': '1.0.2', 'root': False}, {'name': 'spdx-exceptions', 'version': '1.0.4', 'root': False}, {'name': 'validate-npm-package-name', 'version': '2.2.2', 'root': False}, {'name': 'builtins', 'version': '0.0.7', 'root': False}, {'name': 'which', 'version': '1.2.11', 'root': False}, {'name': 'isexe', 'version': '1.1.2', 'root': False}, {'name': 'write-file-atomic', 'version': '1.2.0', 'root': False}, {'name': 'npm-normalize-package-bin', 'version': '1.0.1', 'root': False}, {'name': 'npm-run-path', 'version': '2.0.2', 'root': False}, {'name': 'nyc', 'version': '7.1.0', 'root': False}, {'name': 'align-text', 'version': '0.1.4', 'root': False}, {'name': 'amdefine', 'version': '1.0.0', 'root': False}, {'name': 'append-transform', 'version': '0.3.0', 'root': False}, {'name': 'arr-diff', 'version': '2.0.0', 'root': False}, {'name': 'arr-flatten', 'version': '1.0.1', 'root': False}, {'name': 'array-unique', 'version': '0.2.1', 'root': False}, {'name': 'babel-code-frame', 'version': '6.11.0', 'root': False}, {'name': 'babel-generator', 'version': '6.11.4', 'root': False}, {'name': 'babel-messages', 'version': '6.8.0', 'root': False}, {'name': 'babel-runtime', 'version': '6.9.2', 'root': False}, {'name': 'babel-template', 'version': '6.9.0', 'root': False}, {'name': 'babel-traverse', 'version': '6.11.4', 'root': False}, {'name': 'babel-types', 'version': '6.11.1', 'root': False}, {'name': 'babylon', 'version': '6.8.4', 'root': False}, {'name': 'braces', 'version': '1.8.5', 'root': False, 'cves_index': [76, 77]}, {'name': 'caching-transform', 'version': '1.0.1', 'root': False}, {'name': 'camelcase', 'version': '1.2.1', 'root': False}, {'name': 'center-align', 'version': '0.1.3', 'root': False}, {'name': 'cliui', 'version': '2.1.0', 'root': False}, {'name': 'wordwrap', 'version': '0.0.2', 'root': False}, {'name': 'commondir', 'version': '1.0.1', 'root': False}, {'name': 'convert-source-map', 'version': '1.3.0', 'root': False}, {'name': 'core-js', 'version': '2.4.1', 'root': False}, {'name': 'cross-spawn', 'version': '4.0.0', 'root': False}, {'name': 'default-require-extensions', 'version': '1.0.0', 'root': False}, {'name': 'detect-indent', 'version': '3.0.1', 'root': False}, {'name': 'error-ex', 'version': '1.3.0', 'root': False}, {'name': 'esutils', 'version': '2.0.2', 'root': False}, {'name': 'expand-brackets', 'version': '0.1.5', 'root': False}, {'name': 'expand-range', 'version': '1.8.2', 'root': False}, {'name': 'extglob', 'version': '0.3.2', 'root': False}, {'name': 'filename-regex', 'version': '2.0.0', 'root': False}, {'name': 'fill-range', 'version': '2.2.3', 'root': False}, {'name': 'find-cache-dir', 'version': '0.1.1', 'root': False}, {'name': 'for-in', 'version': '0.1.5', 'root': False}, {'name': 'for-own', 'version': '0.1.4', 'root': False}, {'name': 'foreground-child', 'version': '1.5.3', 'root': False}, {'name': 'get-caller-file', 'version': '1.0.1', 'root': False}, {'name': 'glob', 'version': '7.0.5', 'root': False}, {'name': 'glob-base', 'version': '0.3.0', 'root': False}, {'name': 'glob-parent', 'version': '2.0.0', 'root': False, 'cves_index': [112]}, {'name': 'globals', 'version': '8.18.0', 'root': False}, {'name': 'graceful-fs', 'version': '4.1.4', 'root': False}, {'name': 'handlebars', 'version': '4.0.5', 'root': False, 'cves_index': [96, 97, 98, 99, 100, 101, 92, 93, 94, 95]}, {'name': 'source-map', 'version': '0.4.4', 'root': False}, {'name': 'has-flag', 'version': '1.0.0', 'root': False}, {'name': 'inherits', 'version': '2.0.1', 'root': False}, {'name': 'invariant', 'version': '2.2.1', 'root': False}, {'name': 'is-buffer', 'version': '1.1.3', 'root': False}, {'name': 'is-dotfile', 'version': '1.0.2', 'root': False}, {'name': 'is-equal-shallow', 'version': '0.1.3', 'root': False}, {'name': 'is-extglob', 'version': '1.0.0', 'root': False}, {'name': 'is-finite', 'version': '1.0.1', 'root': False}, {'name': 'is-glob', 'version': '2.0.1', 'root': False}, {'name': 'is-number', 'version': '2.1.0', 'root': False}, {'name': 'is-posix-bracket', 'version': '0.1.1', 'root': False}, {'name': 'is-primitive', 'version': '2.0.0', 'root': False}, {'name': 'isobject', 'version': '2.1.0', 'root': False}, {'name': 'istanbul-lib-coverage', 'version': '1.0.0-alpha.4', 'root': False}, {'name': 'istanbul-lib-hook', 'version': '1.0.0-alpha.4', 'root': False}, {'name': 'istanbul-lib-instrument', 'version': '1.1.0-alpha.4', 'root': False}, {'name': 'istanbul-lib-report', 'version': '1.0.0-alpha.3', 'root': False}, {'name': 'supports-color', 'version': '3.1.2', 'root': False}, {'name': 'istanbul-lib-source-maps', 'version': '1.0.0-alpha.10', 'root': False}, {'name': 'istanbul-reports', 'version': '1.0.0-alpha.8', 'root': False, 'cves_index': [90]}, {'name': 'js-tokens', 'version': '2.0.0', 'root': False}, {'name': 'kind-of', 'version': '3.0.3', 'root': False}, {'name': 'lazy-cache', 'version': '1.0.4', 'root': False}, {'name': 'lodash', 'version': '4.13.1', 'root': False, 'cves_index': [103, 104, 105, 106, 107, 108, 109]}, {'name': 'lodash.assign', 'version': '4.0.9', 'root': False}, {'name': 'lodash.keys', 'version': '4.0.7', 'root': False}, {'name': 'lodash.rest', 'version': '4.0.3', 'root': False}, {'name': 'longest', 'version': '1.0.1', 'root': False}, {'name': 'loose-envify', 'version': '1.2.0', 'root': False}, {'name': 'js-tokens', 'version': '1.0.3', 'root': False}, {'name': 'lru-cache', 'version': '4.0.1', 'root': False}, {'name': 'md5-hex', 'version': '1.3.0', 'root': False}, {'name': 'md5-o-matic', 'version': '0.1.1', 'root': False}, {'name': 'micromatch', 'version': '2.3.11', 'root': False}, {'name': 'minimatch', 'version': '3.0.2', 'root': False, 'cves_index': [110, 111]}, {'name': 'normalize-path', 'version': '2.0.1', 'root': False}, {'name': 'object.omit', 'version': '2.0.0', 'root': False}, {'name': 'once', 'version': '1.3.3', 'root': False}, {'name': 'os-locale', 'version': '1.4.0', 'root': False}, {'name': 'parse-glob', 'version': '3.0.4', 'root': False}, {'name': 'parse-json', 'version': '2.2.0', 'root': False}, {'name': 'path-exists', 'version': '2.1.0', 'root': False}, {'name': 'path-parse', 'version': '1.0.5', 'root': False, 'cves_index': [102]}, {'name': 'path-type', 'version': '1.1.0', 'root': False}, {'name': 'pify', 'version': '2.3.0', 'root': False}, {'name': 'pkg-dir', 'version': '1.0.0', 'root': False}, {'name': 'pkg-up', 'version': '1.0.0', 'root': False}, {'name': 'preserve', 'version': '0.2.0', 'root': False}, {'name': 'pseudomap', 'version': '1.0.2', 'root': False}, {'name': 'randomatic', 'version': '1.1.5', 'root': False, 'cves_index': [91]}, {'name': 'read-pkg', 'version': '1.1.0', 'root': False}, {'name': 'read-pkg-up', 'version': '1.0.1', 'root': False}, {'name': 'regenerator-runtime', 'version': '0.9.5', 'root': False}, {'name': 'regex-cache', 'version': '0.4.3', 'root': False}, {'name': 'repeat-element', 'version': '1.1.2', 'root': False}, {'name': 'repeat-string', 'version': '1.5.4', 'root': False}, {'name': 'repeating', 'version': '1.1.3', 'root': False}, {'name': 'require-directory', 'version': '2.1.1', 'root': False}, {'name': 'require-main-filename', 'version': '1.0.1', 'root': False}, {'name': 'resolve-from', 'version': '2.0.0', 'root': False}, {'name': 'right-align', 'version': '0.1.3', 'root': False}, {'name': 'source-map', 'version': '0.5.6', 'root': False}, {'name': 'spawn-wrap', 'version': '1.2.4', 'root': False}, {'name': 'signal-exit', 'version': '2.1.2', 'root': False}, {'name': 'spdx-exceptions', 'version': '1.0.5', 'root': False}, {'name': 'spdx-license-ids', 'version': '1.2.1', 'root': False}, {'name': 'string-width', 'version': '1.0.1', 'root': False}, {'name': 'strip-bom', 'version': '2.0.0', 'root': False}, {'name': 'test-exclude', 'version': '1.1.0', 'root': False}, {'name': 'to-fast-properties', 'version': '1.0.2', 'root': False}, {'name': 'uglify-js', 'version': '2.7.0', 'root': False, 'cves_index': [89]}, {'name': 'yargs', 'version': '3.10.0', 'root': False}, {'name': 'uglify-to-browserify', 'version': '1.0.2', 'root': False}, {'name': 'which', 'version': '1.2.10', 'root': False}, {'name': 'which-module', 'version': '1.0.0', 'root': False}, {'name': 'window-size', 'version': '0.1.0', 'root': False}, {'name': 'wrap-ansi', 'version': '2.0.0', 'root': False}, {'name': 'write-file-atomic', 'version': '1.1.4', 'root': False}, {'name': 'y18n', 'version': '3.2.1', 'root': False, 'cves_index': [117]}, {'name': 'yallist', 'version': '2.0.0', 'root': False}, {'name': 'yargs', 'version': '4.8.1', 'root': False}, {'name': 'window-size', 'version': '0.2.0', 'root': False}, {'name': 'yargs-parser', 'version': '2.4.1', 'root': False, 'cves_index': [114]}, {'name': 'camelcase', 'version': '3.0.0', 'root': False}, {'name': 'oauth-sign', 'version': '0.9.0', 'root': False}, {'name': 'object-copy', 'version': '0.1.0', 'root': False}, {'name': 'object.defaults', 'version': '1.1.0', 'root': False}, {'name': 'object.map', 'version': '1.0.1', 'root': False}, {'name': 'onetime', 'version': '1.1.0', 'root': False}, {'name': 'only-shallow', 'version': '1.2.0', 'root': False}, {'name': 'opener', 'version': '1.5.2', 'root': False}, {'name': 'options', 'version': '0.0.6', 'root': False}, {'name': 'ora', 'version': '0.2.3', 'root': False}, {'name': 'os-homedir', 'version': '1.0.2', 'root': False}, {'name': 'os-tmpdir', 'version': '1.0.2', 'root': False}, {'name': 'osenv', 'version': '0.1.5', 'root': False}, {'name': 'p-finally', 'version': '1.0.0', 'root': False}, {'name': 'p-map', 'version': '1.2.0', 'root': False}, {'name': 'package-json', 'version': '4.0.1', 'root': False}, {'name': 'pad-stream', 'version': '1.2.0', 'root': False}, {'name': 'parse-filepath', 'version': '1.0.2', 'root': False}, {'name': 'parse-passwd', 'version': '1.0.0', 'root': False}, {'name': 'path-key', 'version': '3.1.1', 'root': False}, {'name': 'path-parse', 'version': '1.0.7', 'root': False}, {'name': 'path-root', 'version': '0.1.1', 'root': False}, {'name': 'path-root-regex', 'version': '0.1.2', 'root': False}, {'name': 'pend', 'version': '1.2.0', 'root': False}, {'name': 'performance-now', 'version': '2.1.0', 'root': False}, {'name': 'picomatch', 'version': '2.3.1', 'root': False}, {'name': 'prepend-http', 'version': '1.0.4', 'root': False}, {'name': 'colors', 'version': '1.4.0', 'root': False}, {'name': 'process-nextick-args', 'version': '2.0.1', 'root': False}, {'name': 'revalidator', 'version': '0.1.8', 'root': False}, {'name': 'psl', 'version': '1.8.0', 'root': False}, {'name': 'pstree.remy', 'version': '1.1.8', 'root': False}, {'name': 'pump', 'version': '2.0.1', 'root': False}, {'name': 'pumpify', 'version': '1.5.1', 'root': False}, {'name': 'punycode', 'version': '2.1.1', 'root': False}, {'name': 'q', 'version': '1.5.1', 'root': False}, {'name': 'querystring', 'version': '0.2.0', 'root': False}, {'name': 'ramda', 'version': '0.24.1', 'root': False, 'cves_index': [113]}, {'name': 'random-bytes', 'version': '1.0.0', 'root': False}, {'name': 'rc', 'version': '1.2.8', 'root': False}, {'name': 'strip-json-comments', 'version': '2.0.1', 'root': False}, {'name': 'read-package-json', 'version': '2.1.2', 'root': False}, {'name': 'readable-stream', 'version': '2.3.7', 'root': False}, {'name': 'string_decoder', 'version': '1.1.1', 'root': False}, {'name': 'readdir-scoped-modules', 'version': '1.1.0', 'root': False}, {'name': 'rechoir', 'version': '0.7.1', 'root': False}, {'name': 'redent', 'version': '1.0.0', 'root': False}, {'name': 'safe-regex', 'version': '1.1.0', 'root': False}, {'name': 'registry-auth-token', 'version': '3.4.0', 'root': False}, {'name': 'registry-url', 'version': '3.1.0', 'root': False}, {'name': 'repeating', 'version': '2.0.1', 'root': False}, {'name': 'request', 'version': '2.88.0', 'root': False}, {'name': 'qs', 'version': '6.5.3', 'root': False}, {'name': 'request-progress', 'version': '3.0.0', 'root': False}, {'name': 'semver', 'version': '5.7.1', 'root': False}, {'name': 'resolve', 'version': '1.22.0', 'root': False}, {'name': 'resolve-dir', 'version': '1.0.1', 'root': False}, {'name': 'resolve-url', 'version': '0.2.1', 'root': False}, {'name': 'restore-cursor', 'version': '1.0.1', 'root': False}, {'name': 'resumer', 'version': '0.0.0', 'root': False}, {'name': 'through', 'version': '2.3.8', 'root': False}, {'name': 'ret', 'version': '0.1.15', 'root': False}, {'name': 'retire', 'version': '1.1.6', 'root': False}, {'name': 'commander', 'version': '2.5.1', 'root': False}, {'name': 'underscore', 'version': '1.8.3', 'root': False}, {'name': 'rxjs', 'version': '5.5.12', 'root': False}, {'name': 'safe-json-parse', 'version': '1.0.1', 'root': False}, {'name': 'selenium-webdriver', 'version': '2.53.3', 'root': True}, {'name': 'tmp', 'version': '0.0.24', 'root': False}, {'name': 'semver-diff', 'version': '2.1.0', 'root': False}, {'name': 'serve-favicon', 'version': '2.5.0', 'root': True}, {'name': 'ms', 'version': '2.1.1', 'root': False}, {'name': 'safe-buffer', 'version': '5.1.1', 'root': False}, {'name': 'shebang-command', 'version': '2.0.0', 'root': False}, {'name': 'shebang-regex', 'version': '3.0.0', 'root': False}, {'name': 'shelljs', 'version': '0.3.0', 'root': False, 'cves_index': [115, 116]}, {'name': 'should', 'version': '8.4.0', 'root': True}, {'name': 'should-equal', 'version': '0.8.0', 'root': False}, {'name': 'should-format', 'version': '0.3.2', 'root': False}, {'name': 'should-type', 'version': '0.2.0', 'root': False}, {'name': 'strip-json-comments', 'version': '0.1.3', 'root': False}, {'name': 'sigmund', 'version': '1.0.1', 'root': False}, {'name': 'signal-exit', 'version': '3.0.7', 'root': False}, {'name': 'slice-ansi', 'version': '0.0.4', 'root': False}, {'name': 'source-map', 'version': '0.5.7', 'root': False}, {'name': 'source-map-resolve', 'version': '0.5.3', 'root': False}, {'name': 'use', 'version': '3.1.1', 'root': False}, {'name': 'snapdragon-util', 'version': '3.0.1', 'root': False}, {'name': 'source-map-url', 'version': '0.4.1', 'root': False}, {'name': 'urix', 'version': '0.1.0', 'root': False}, {'name': 'spdx-correct', 'version': '3.1.1', 'root': False}, {'name': 'spdx-exceptions', 'version': '2.3.0', 'root': False}, {'name': 'spdx-expression-parse', 'version': '3.0.1', 'root': False}, {'name': 'spdx-license-ids', 'version': '3.0.11', 'root': False}, {'name': 'split2', 'version': '1.1.1', 'root': False}, {'name': 'sprintf-js', 'version': '1.1.2', 'root': False}, {'name': 'sshpk', 'version': '1.17.0', 'root': False}, {'name': 'stack-utils', 'version': '0.4.0', 'root': False}, {'name': 'stream-shift', 'version': '1.0.1', 'root': False}, {'name': 'stream-to-observable', 'version': '0.1.0', 'root': False}, {'name': 'string-template', 'version': '0.2.1', 'root': False}, {'name': 'stringstream', 'version': '0.0.6', 'root': False}, {'name': 'strip-eof', 'version': '1.0.0', 'root': False}, {'name': 'strip-indent', 'version': '1.0.1', 'root': False}, {'name': 'supports-color', 'version': '5.5.0', 'root': False}, {'name': 'supports-preserve-symlinks-flag', 'version': '1.0.0', 'root': False}, {'name': 'swig', 'version': '1.4.2', 'root': True, 'vulnerable_dependencies': [113, 1017]}, {'name': 'uglify-js', 'version': '2.4.24', 'root': False, 'cves_index': [140, 141]}, {'name': 'symbol-observable', 'version': '1.0.1', 'root': False}, {'name': 'tap', 'version': '7.1.2', 'root': False}, {'name': 'tap-mocha-reporter', 'version': '2.0.1', 'root': False, 'cves_index': [120, 119]}, {'name': 'tap-parser', 'version': '2.2.3', 'root': False}, {'name': 'deep-equal', 'version': '0.1.2', 'root': False}, {'name': 'term-size', 'version': '1.2.0', 'root': False}, {'name': 'cross-spawn', 'version': '5.1.0', 'root': False}, {'name': 'execa', 'version': '0.7.0', 'root': False}, {'name': 'throttleit', 'version': '1.0.0', 'root': False}, {'name': 'through2', 'version': '2.0.5', 'root': False}, {'name': 'timed-out', 'version': '4.0.1', 'root': False}, {'name': 'tiny-lr', 'version': '1.1.1', 'root': False}, {'name': 'tmatch', 'version': '2.0.1', 'root': False}, {'name': 'tmp', 'version': '0.1.0', 'root': False}, {'name': 'to-iso-string', 'version': '0.0.2', 'root': False}, {'name': 'touch', 'version': '3.1.0', 'root': False}, {'name': 'nopt', 'version': '1.0.10', 'root': False}, {'name': 'tough-cookie', 'version': '2.4.3', 'root': False}, {'name': 'trim-newlines', 'version': '1.0.0', 'root': False, 'cves_index': [139]}, {'name': 'tunnel-agent', 'version': '0.6.0', 'root': False}, {'name': 'tweetnacl', 'version': '0.14.5', 'root': False}, {'name': 'source-map', 'version': '0.1.34', 'root': False}, {'name': 'yargs', 'version': '3.5.4', 'root': False}, {'name': 'ultron', 'version': '1.0.2', 'root': False}, {'name': 'unc-path-regex', 'version': '0.1.2', 'root': False}, {'name': 'undefsafe', 'version': '2.0.5', 'root': False}, {'name': 'underscore', 'version': '1.13.2', 'root': True}, {'name': 'underscore.string', 'version': '3.3.6', 'root': False}, {'name': 'unicode-length', 'version': '1.0.3', 'root': False}, {'name': 'unique-string', 'version': '1.0.0', 'root': False}, {'name': 'universalify', 'version': '0.1.2', 'root': False}, {'name': 'has-value', 'version': '0.3.1', 'root': False}, {'name': 'has-values', 'version': '0.1.4', 'root': False}, {'name': 'untildify', 'version': '3.0.3', 'root': False}, {'name': 'unzip-response', 'version': '2.0.1', 'root': False}, {'name': 'update-notifier', 'version': '2.5.0', 'root': False}, {'name': 'uri-js', 'version': '4.4.1', 'root': False}, {'name': 'url', 'version': '0.11.0', 'root': False}, {'name': 'punycode', 'version': '1.3.2', 'root': False}, {'name': 'url-parse-lax', 'version': '1.0.0', 'root': False}, {'name': 'async', 'version': '0.9.2', 'root': False}, {'name': 'deep-equal', 'version': '0.2.2', 'root': False}, {'name': 'ncp', 'version': '1.0.1', 'root': False}, {'name': 'uuid', 'version': '3.4.0', 'root': False}, {'name': 'v8flags', 'version': '3.2.0', 'root': False}, {'name': 'validate-npm-package-license', 'version': '3.0.4', 'root': False}, {'name': 'verror', 'version': '1.10.0', 'root': False}, {'name': 'walkdir', 'version': '0.0.7', 'root': False}, {'name': 'websocket-driver', 'version': '0.7.4', 'root': False}, {'name': 'websocket-extensions', 'version': '0.1.4', 'root': False}, {'name': 'which', 'version': '2.0.2', 'root': False}, {'name': 'widest-line', 'version': '2.0.1', 'root': False}, {'name': 'window-size', 'version': '0.1.4', 'root': False}, {'name': 'write-file-atomic', 'version': '2.4.3', 'root': False}, {'name': 'ws', 'version': '1.1.5', 'root': False}, {'name': 'xdg-basedir', 'version': '3.0.0', 'root': False}, {'name': 'xml2js', 'version': '0.4.4', 'root': False}, {'name': 'sax', 'version': '0.6.1', 'root': False}, {'name': 'xmlbuilder', 'version': '15.1.1', 'root': False}, {'name': 'xtend', 'version': '4.0.2', 'root': False}, {'name': 'y18n', 'version': '3.2.2', 'root': False}, {'name': 'yallist', 'version': '2.1.2', 'root': False}, {'name': 'yauzl', 'version': '2.10.0', 'root': False}, {'name': 'fd-slicer', 'version': '1.1.0', 'root': False}, {'name': 'zaproxy', 'version': '0.2.0', 'root': True}, {'name': 'asn1', 'version': '0.1.11', 'root': False}, {'name': 'assert-plus', 'version': '0.1.5', 'root': False}, {'name': 'aws-sign2', 'version': '0.5.0', 'root': False}, {'name': 'boom', 'version': '0.4.2', 'root': False}, {'name': 'combined-stream', 'version': '0.0.7', 'root': False}, {'name': 'cryptiles', 'version': '0.2.2', 'root': False, 'cves_index': [131]}, {'name': 'delayed-stream', 'version': '0.0.5', 'root': False}, {'name': 'forever-agent', 'version': '0.5.2', 'root': False}, {'name': 'form-data', 'version': '0.1.4', 'root': False}, {'name': 'hawk', 'version': '1.0.0', 'root': False, 'cves_index': [121, 122]}, {'name': 'hoek', 'version': '0.9.1', 'root': False, 'cves_index': [137, 138]}, {'name': 'http-signature', 'version': '0.10.1', 'root': False}, {'name': 'lodash', 'version': '2.4.2', 'root': False, 'cves_index': [128, 129, 123, 124, 125, 126, 127]}, {'name': 'mime', 'version': '1.2.11', 'root': False, 'cves_index': [118]}, {'name': 'oauth-sign', 'version': '0.3.0', 'root': False}, {'name': 'qs', 'version': '0.6.6', 'root': False, 'cves_index': [132, 133, 134, 135, 136]}, {'name': 'request', 'version': '2.36.0', 'root': False, 'cves_index': [130]}, {'name': 'sntp', 'version': '0.2.4', 'root': False}], 'sourceId': 'ajbara_cli_repo/ScaGoat-main', 'sourceType': 'CLI', 'type': 'Package', 'vulnerabilities': [{'severity': 'high', 'riskFactors': {'High severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2021-3807', 'link': 'https://github.com/advisories/GHSA-93q8-gq69-wqmw', 'description': 'ansi-regex is vulnerable to Inefficient Regular Expression Complexity', 'packageVersion': '3.0.0', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'ansi-regex', 'publishedDate': '2021-09-17T07:15:00Z', 'cvss': 7.5, 'status': 'fixed in 4.1.1'}, {'severity': 'moderate', 'riskFactors': {'Medium severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2020-8244', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2020-8244', 'description': 'A buffer over-read vulnerability exists in bl <4.0.3, <3.0.1, <2.2.1, and <1.2.3 which could allow an attacker to supply user input (even typed) that if it ends up in consume() argument and can become negative, the BufferList state can be corrupted, tricking it into exposing uninitialized memory via regular .slice() calls.', 'packageVersion': '1.0.3', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L', 'packageName': 'bl', 'publishedDate': '2020-08-30T15:15:00Z', 'cvss': 4, 'status': 'fixed in 2.2.1, 1.2.3, 4.0.3, 3.0.1'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2021-43138', 'link': 'https://github.com/advisories/GHSA-fwr7-v2mv-hh25', 'description': 'In Async before 2.6.4 and 3.x before 3.2.2, a malicious user can obtain privileges via the mapValues() method, aka lib/internal/iterator.js createObjectIterator prototype pollution.', 'packageVersion': '2.6.3', 'vector': 'CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H', 'packageName': 'async', 'publishedDate': '2022-04-06T17:15:00Z', 'cvss': 7, 'status': 'fixed in 2.6.4, 3.2.2'}, {'severity': 'high', 'riskFactors': {'Has fix': {}, 'High severity': {}}, 'cveId': 'PRISMA-2021-0034', 'link': '', 'description': 'adm-zip package versions before 0.5.3 are vulnerable to Directory Traversal. It could extract files outside the target folder. origin: https://github.com/cthackers/adm-zip/commit/119dcad6599adccc77982feb14a0c7440fa63013', 'packageVersion': '0.4.4', 'vector': '', 'packageName': 'adm-zip', 'publishedDate': '2021-03-03T11:06:55Z', 'cvss': 0, 'status': 'fixed in 0.5.3'}, {'severity': 'medium', 'riskFactors': {'Has fix': {}, 'Medium severity': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2018-1002204', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2018-1002204', 'description': "adm-zip npm library before 0.4.9 is vulnerable to directory traversal, allowing attackers to write to arbitrary files via a ../ (dot dot slash) in a Zip archive entry that is mishandled during extraction. This vulnerability is also known as \\'Zip-Slip\\'.", 'packageVersion': '0.4.4', 'vector': 'CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N', 'packageName': 'adm-zip', 'publishedDate': '2018-07-25T17:29:00Z', 'cvss': 5.5, 'status': 'fixed in 0.4.9'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2022-21803', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2022-21803', 'description': 'This affects the package nconf before 0.11.4. When using the memory engine, it is possible to store a nested JSON representation of the configuration. The .set() function, that is responsible for setting the configuration properties, is vulnerable to Prototype Pollution. By providing a crafted property, it is possible to modify the properties on the Object.prototype.', 'packageVersion': '0.6.9', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N', 'packageName': 'nconf', 'publishedDate': '2022-04-12T16:15:00Z', 'cvss': 7.5, 'status': 'fixed in 0.11.4'}, {'severity': 'moderate', 'riskFactors': {'Medium severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2019-2391', 'link': 'https://github.com/advisories/GHSA-4jwp-vfvf-657p', 'description': 'Incorrect parsing of certain JSON input may result in js-bson not correctly serializing BSON. This may cause unexpected application behaviour including data disclosure. This issue affects: MongoDB Inc. js-bson library version 1.1.3 and prior to.', 'packageVersion': '1.0.9', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N', 'packageName': 'bson', 'publishedDate': '2020-03-31T14:15:00Z', 'cvss': 4, 'status': 'fixed in 1.1.4'}, {'severity': 'critical', 'riskFactors': {'Critical severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2020-7610', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2020-7610', 'description': "All versions of bson before 1.1.4 are vulnerable to Deserialization of Untrusted Data. The package will ignore an unknown value for an object\\'s _bsotype, leading to cases where an object is serialized as a document rather than the intended BSON type.", 'packageVersion': '1.0.9', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H', 'packageName': 'bson', 'publishedDate': '2020-03-30T19:15:00Z', 'cvss': 9.8, 'status': 'fixed in 1.1.4'}, {'severity': 'medium', 'riskFactors': {'Medium severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2017-16137', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2017-16137', 'description': 'The debug module is vulnerable to regular expression denial of service when untrusted user input is passed into the o formatter. It takes around 50k characters to block for 2 seconds making this a low severity issue.', 'packageVersion': '2.2.0', 'vector': 'CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L', 'packageName': 'debug', 'publishedDate': '2018-06-07T02:29:00Z', 'cvss': 5.3, 'status': 'fixed in 3.1.0, 2.6.9'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'DoS': {}, 'Has fix': {}, 'Remote execution': {}}, 'cveId': 'PRISMA-2022-0049', 'link': 'https://github.com/jonschlinkert/unset-value/pull/12/commits/abb534769f6ea62c3dd988f5ce0a4ebd1f91b56', 'description': 'unset-value package versions before 2.0.1 are vulnerable to Prototype Pollution. unset() function in index.js files allows for access to object prototype properties. An attacker can exploit this to override the behavior of object prototypes, resulting in a possible Denial of Service (DoS), Remote Code Execution (RCE), or other unexpected behavior.', 'packageVersion': '1.0.0', 'vector': '', 'packageName': 'unset-value', 'publishedDate': '2022-02-21T10:09:35Z', 'cvss': 8, 'status': 'fixed in 2.0.1'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2020-28469', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2020-28469', 'description': 'This affects the package glob-parent before 5.1.2. The enclosure regex used to check for strings ending in enclosure containing path separator.', 'packageVersion': '3.1.0', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'glob-parent', 'publishedDate': '2021-06-03T16:15:00Z', 'cvss': 7.5, 'status': 'fixed in 5.1.2'}, {'severity': 'medium', 'riskFactors': {'Attack vector: network': {}, 'Has fix': {}, 'Medium severity': {}}, 'cveId': 'CVE-2020-7598', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2020-7598', 'description': 'minimist before 1.2.2 could be tricked into adding or modifying properties of Object.prototype using a \\"constructor\\" or \\"__proto__\\" payload.', 'packageVersion': '0.0.10', 'vector': 'CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L', 'packageName': 'minimist', 'publishedDate': '2020-03-11T23:15:00Z', 'cvss': 5.6, 'status': 'fixed in 1.2.2'}, {'severity': 'critical', 'riskFactors': {'Critical severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2021-44906', 'link': 'https://github.com/advisories/GHSA-xvch-5gv4-984h', 'description': 'Minimist <=1.2.5 is vulnerable to Prototype Pollution via file index.js, function setKey() (lines 69-95).', 'packageVersion': '0.0.10', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H', 'packageName': 'minimist', 'publishedDate': '2022-03-17T16:15:00Z', 'cvss': 9.8, 'status': 'fixed in 1.2.6'}, {'severity': 'low', 'riskFactors': {'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2022-38900', 'link': 'https://github.com/advisories/GHSA-w573-4hg7-7wgq', 'description': 'decode-uri-component 0.2.0 is vulnerable to Improper Input Validation resulting in DoS.', 'packageVersion': '0.2.0', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'decode-uri-component', 'publishedDate': '2022-11-28T15:30:24Z', 'cvss': 1, 'status': 'fixed in 0.2.1'}, {'severity': 'critical', 'riskFactors': {'Critical severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2018-1000620', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2018-1000620', 'description': 'Eran Hammer cryptiles version 4.1.1 earlier contains a CWE-331: Insufficient Entropy vulnerability in randomDigits() method that can result in An attacker is more likely to be able to brute force something that was supposed to be random.. This attack appear to be exploitable via Depends upon the calling application.. This vulnerability appears to have been fixed in 4.1.2.', 'packageVersion': '2.0.5', 'vector': 'CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H', 'packageName': 'cryptiles', 'publishedDate': '2018-07-19T00:00:00Z', 'cvss': 9, 'status': 'fixed in 4.1.2'}, {'severity': 'moderate', 'riskFactors': {'Has fix': {}, 'Medium severity': {}, 'DoS': {}}, 'cveId': 'GHSA-2pr6-76vf-7546', 'link': '', 'description': 'Versions of `js-yaml` prior to 3.13.0 are vulnerable to Denial of Service. By parsing a carefully-crafted YAML file, the node process stalls and may exhaust system resources leading to a Denial of Service.   ## Recommendation  Upgrade to version 3.13.0.', 'packageVersion': '3.6.1', 'vector': '', 'packageName': 'js-yaml', 'publishedDate': '2019-06-05T14:35:29Z', 'cvss': 4, 'status': 'fixed in 3.13.0'}, {'severity': 'high', 'riskFactors': {'Has fix': {}, 'High severity': {}}, 'cveId': 'GHSA-8j8c-7jfh-h6hx', 'link': '', 'description': 'Versions of `js-yaml` prior to 3.13.1 are vulnerable to Code Injection. The `load()` function may execute arbitrary code injected through a malicious YAML file. Objects that have `toString` as key, JavaScript code as value and are used as explicit mapping keys allow attackers to execute the supplied code through the `load()` function. The `safeLoad()` function is unaffected.  An example payload is  `{ toString: !<tag:yaml.org,2002:js/function> \\\'function (){return Date.now()}\\\' } : 1`  which returns the object  {   \\"1553107949161\\": 1 }   ## Recommendation  Upgrade to version 3.13.1.', 'packageVersion': '3.6.1', 'vector': '', 'packageName': 'js-yaml', 'publishedDate': '2019-06-04T20:14:07Z', 'cvss': 7, 'status': 'fixed in 3.13.1'}, {'severity': 'medium', 'riskFactors': {'Has fix': {}, 'Medium severity': {}}, 'cveId': 'PRISMA-2021-0070', 'link': 'https://github.com/cypress-io/cypress/pull/16165', 'description': 'cypress package versions before 7.2.0 are vulnerable to Incorrect Default Permissions. contextIsolation setting not being set within webpreferences, so an attacker can insert JavaScript as part of test and can execute arbitrary code.', 'packageVersion': '3.8.3', 'vector': '', 'packageName': 'cypress', 'publishedDate': '2021-05-18T09:29:31Z', 'cvss': 0, 'status': 'fixed in 7.2.0'}, {'severity': 'moderate', 'riskFactors': {'Has fix': {}, 'Medium severity': {}}, 'cveId': 'GHSA-xc7v-wxcw-j472', 'link': '', 'description': "Versions of `tunnel-agent` before 0.6.0 are vulnerable to memory exposure.  This is exploitable if user supplied input is provided to the auth value and is a number.  Proof-of-concept: ```js require(\\'request\\')({   method: \\'GET\\',   uri: \\'http://www.example.com\\',   tunnel: true,   proxy:{     protocol: \\'http:\\',     host:\\'127.0.0.1\\',     port:8080,     auth:USERSUPPLIEDINPUT // number   } }); ```   ## Recommendation  Update to version 0.6.0 or later.", 'packageVersion': '0.4.3', 'vector': '', 'packageName': 'tunnel-agent', 'publishedDate': '2019-06-03T17:08:26Z', 'cvss': 4, 'status': 'fixed in 0.6.0'}, {'severity': 'high', 'riskFactors': {'Attack vector: network': {}, 'Has fix': {}, 'High severity': {}}, 'cveId': 'CVE-2020-8203', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2020-8203', 'description': 'Prototype pollution attack when using _.zipObjectDeep in lodash before 4.17.20.', 'packageVersion': '4.17.15', 'vector': 'CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H', 'packageName': 'lodash', 'publishedDate': '2020-07-15T17:15:00Z', 'cvss': 7.4, 'status': 'fixed in 4.17.20'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2021-23337', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2021-23337', 'description': 'Lodash versions prior to 4.17.21 are vulnerable to Command Injection via the template function.', 'packageVersion': '4.17.15', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H', 'packageName': 'lodash', 'publishedDate': '2021-02-15T13:15:00Z', 'cvss': 7.2, 'status': 'fixed in 4.17.21'}, {'severity': 'medium', 'riskFactors': {'Medium severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2020-28500', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2020-28500', 'description': 'Lodash versions prior to 4.17.21 are vulnerable to Regular Expression Denial of Service (ReDoS) via the toNumber, trim and trimEnd functions.', 'packageVersion': '4.17.15', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L', 'packageName': 'lodash', 'publishedDate': '2021-02-15T11:15:00Z', 'cvss': 5.3, 'status': 'fixed in 4.17.21'}, {'severity': 'medium', 'riskFactors': {'Attack vector: network': {}, 'Has fix': {}, 'Medium severity': {}}, 'cveId': 'CVE-2020-7598', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2020-7598', 'description': 'minimist before 1.2.2 could be tricked into adding or modifying properties of Object.prototype using a \\"constructor\\" or \\"__proto__\\" payload.', 'packageVersion': '1.2.0', 'vector': 'CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L', 'packageName': 'minimist', 'publishedDate': '2020-03-11T23:15:00Z', 'cvss': 5.6, 'status': 'fixed in 1.2.2'}, {'severity': 'critical', 'riskFactors': {'Critical severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2021-44906', 'link': 'https://github.com/advisories/GHSA-xvch-5gv4-984h', 'description': 'Minimist <=1.2.5 is vulnerable to Prototype Pollution via file index.js, function setKey() (lines 69-95).', 'packageVersion': '1.2.0', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H', 'packageName': 'minimist', 'publishedDate': '2022-03-17T16:15:00Z', 'cvss': 9.8, 'status': 'fixed in 1.2.6'}, {'severity': 'high', 'riskFactors': {'Has fix': {}, 'High severity': {}, 'DoS': {}}, 'cveId': 'GHSA-h6ch-v84p-w6p9', 'link': 'https://github.com/advisories/GHSA-h6ch-v84p-w6p9', 'description': 'A vulnerability was found in diff before v3.5.0, the affected versions of this package are vulnerable to Regular Expression Denial of Service (ReDoS) attacks.', 'packageVersion': '1.4.0', 'vector': '', 'packageName': 'diff', 'publishedDate': '2019-06-13T18:58:54Z', 'cvss': 7, 'status': 'fixed in 3.5.0'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2022-21803', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2022-21803', 'description': 'This affects the package nconf before 0.11.4. When using the memory engine, it is possible to store a nested JSON representation of the configuration. The .set() function, that is responsible for setting the configuration properties, is vulnerable to Prototype Pollution. By providing a crafted property, it is possible to modify the properties on the Object.prototype.', 'packageVersion': '0.10.0', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N', 'packageName': 'nconf', 'publishedDate': '2022-04-12T16:15:00Z', 'cvss': 7.5, 'status': 'fixed in 0.11.4'}, {'severity': 'medium', 'riskFactors': {'Attack vector: network': {}, 'Has fix': {}, 'Medium severity': {}}, 'cveId': 'CVE-2020-7598', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2020-7598', 'description': 'minimist before 1.2.2 could be tricked into adding or modifying properties of Object.prototype using a \\"constructor\\" or \\"__proto__\\" payload.', 'packageVersion': '0.0.8', 'vector': 'CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L', 'packageName': 'minimist', 'publishedDate': '2020-03-11T23:15:00Z', 'cvss': 5.6, 'status': 'fixed in 1.2.2'}, {'severity': 'critical', 'riskFactors': {'Critical severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2021-44906', 'link': 'https://github.com/advisories/GHSA-xvch-5gv4-984h', 'description': 'Minimist <=1.2.5 is vulnerable to Prototype Pollution via file index.js, function setKey() (lines 69-95).', 'packageVersion': '0.0.8', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H', 'packageName': 'minimist', 'publishedDate': '2022-03-17T16:15:00Z', 'cvss': 9.8, 'status': 'fixed in 1.2.6'}, {'severity': 'moderate', 'riskFactors': {'Attack vector: network': {}, 'Has fix': {}, 'Medium severity': {}}, 'cveId': 'CVE-2017-16026', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2017-16026', 'description': 'Request is an http client. If a request is made using ```multipart```, and the body type is a ```number```, then the specified number of non-zero memory is passed in the body. This affects Request >=2.2.6 <2.47.0 || >2.51.0 <=2.67.0.', 'packageVersion': '2.67.0', 'vector': 'CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N', 'packageName': 'request', 'publishedDate': '2018-06-04T19:29:00Z', 'cvss': 4, 'status': 'fixed in 2.68.0, 2.68.0'}, {'severity': 'medium', 'riskFactors': {'Has fix': {}, 'Medium severity': {}}, 'cveId': 'PRISMA-2022-0087', 'link': 'https://github.com/ljharb/qs/issues/200', 'description': "qs package versions before 6.3.1 are vulnerable to Prototype Pollution. It\\'s a bypass for CVE-2017-1000048, that only fixed ]=toString, but not fixed  [=toString. So it is possible to override prototype properties such as toString() for a nested object which exceeds the depth limit even when allowPrototypes is set to false.", 'packageVersion': '5.2.1', 'vector': '', 'packageName': 'qs', 'publishedDate': '2022-03-17T09:41:42Z', 'cvss': 5.9, 'status': 'fixed in 6.3.1'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2022-24999', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2022-24999', 'description': 'qs before 6.10.3, as used in Express before 4.17.3 and other products, allows attackers to cause a Node process hang for an Express application because an __ proto__ key can be used. In many typical Express use cases, an unauthenticated remote attacker can place the attack payload in the query string of the URL that is used to visit the application, such as a[__proto__]=b&a[__proto__]&a[length]=100000000. The fix was backported to qs 6.9.7, 6.8.3, 6.7.3, 6.6.1, 6.5.3, 6.4.1, 6.3.3, and 6.2.4 (and therefore Express 4.17.3, which has \\"deps: qs@6.9.7\\" in its release description, is not vulnerable).', 'packageVersion': '5.2.1', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'qs', 'publishedDate': '2022-11-26T22:15:00Z', 'cvss': 7.5, 'status': 'fixed in 6.10.3'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2017-1000048', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2017-1000048', 'description': "the web framework using ljharb\\'s qs module older than v6.3.2, v6.2.3, v6.1.2, and v6.0.4 is vulnerable to a DoS. A malicious user can send a evil request to cause the web framework crash.", 'packageVersion': '5.2.1', 'vector': 'CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'qs', 'publishedDate': '2017-03-01T00:00:00Z', 'cvss': 7, 'status': 'fixed in 6.3.2, 6.2.3, 6.1.2, 6.0.4'}, {'severity': 'high', 'riskFactors': {'Has fix': {}, 'High severity': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2022-1537', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2022-1537', 'description': "file.copy operations in GruntJS are vulnerable to a TOCTOU race condition leading to arbitrary file write in GitHub repository gruntjs/grunt prior to 1.5.3. This vulnerability is capable of arbitrary file writes which can lead to local privilege escalation to the GruntJS user if a lower-privileged user has write access to both source and destination directories as the lower-privileged user can create a symlink to the GruntJS user\\'s .bashrc file or replace /etc/shadow file if the GruntJS user is root.", 'packageVersion': '1.4.1', 'vector': 'CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H', 'packageName': 'grunt', 'publishedDate': '2022-05-10T14:15:00Z', 'cvss': 7, 'status': 'fixed in 1.5.3'}, {'severity': 'medium', 'riskFactors': {'Medium severity': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2022-0436', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2022-0436', 'description': 'Path Traversal in GitHub repository gruntjs/grunt prior to 1.5.2.', 'packageVersion': '1.4.1', 'vector': 'CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N', 'packageName': 'grunt', 'publishedDate': '2022-04-12T21:15:00Z', 'cvss': 5.5, 'status': 'fixed in 1.5.2'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2018-3728', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2018-3728', 'description': 'hoek node module before 4.2.0 and 5.0.x before 5.0.3 suffers from a Modification of Assumed-Immutable Data (MAID) vulnerability via \\\'merge\\\' and \\\'applyToDefaults\\\' functions, which allows a malicious user to modify the prototype of \\"Object\\" via __proto__, causing the addition or modification of an existing property that will exist on all objects.', 'packageVersion': '2.16.3', 'vector': 'CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H', 'packageName': 'hoek', 'publishedDate': '2018-03-30T19:29:00Z', 'cvss': 8.8, 'status': 'fixed in 5.0.3, 4.2.0'}, {'severity': 'high', 'riskFactors': {'Attack vector: network': {}, 'Has fix': {}, 'High severity': {}}, 'cveId': 'CVE-2020-36604', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2020-36604', 'description': 'hoek before 8.5.1 and 9.x before 9.0.3 allows prototype poisoning in the clone function.', 'packageVersion': '2.16.3', 'vector': 'CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H', 'packageName': 'hoek', 'publishedDate': '2022-09-23T06:15:00Z', 'cvss': 8.1, 'status': 'fixed in 9.0.3, 8.5.1'}, {'severity': 'moderate', 'riskFactors': {'Has fix': {}, 'Medium severity': {}}, 'cveId': 'GHSA-c3m8-x3cg-qm2c', 'link': '', 'description': "Versions of `helmet-csp` before to 2.9.1 are vulnerable to a Configuration Override affecting the application\\'s Content Security Policy (CSP). The package\\'s browser sniffing for Firefox deletes the `default-src` CSP policy, which is the fallback policy. This allows an attacker to remove an application\\'s default CSP, possibly rendering the application vulnerable to Cross-Site Scripting.   ## Recommendation  Upgrade to version 2.9.1 or later. Setting the `browserSniff` configuration to `false` in vulnerable versions also mitigates the issue.", 'packageVersion': '1.2.2', 'vector': '', 'packageName': 'helmet-csp', 'publishedDate': '2020-09-03T20:39:53Z', 'cvss': 4, 'status': 'fixed in 2.9.1'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2021-43138', 'link': 'https://github.com/advisories/GHSA-fwr7-v2mv-hh25', 'description': 'In Async before 2.6.4 and 3.x before 3.2.2, a malicious user can obtain privileges via the mapValues() method, aka lib/internal/iterator.js createObjectIterator prototype pollution.', 'packageVersion': '2.6.1', 'vector': 'CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H', 'packageName': 'async', 'publishedDate': '2022-04-06T17:15:00Z', 'cvss': 7, 'status': 'fixed in 2.6.4, 3.2.2'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2022-29167', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2022-29167', 'description': "Hawk is an HTTP authentication scheme providing mechanisms for making authenticated HTTP requests with partial cryptographic verification of the request and response, covering the HTTP method, request URI, host, and optionally the request payload. Hawk used a regular expression to parse `Host` HTTP header (`Hawk.utils.parseHost()`), which was subject to regular expression DoS attack - meaning each added character in the attacker\\'s input increases the computation time exponentially. `parseHost()` was patched in `9.0.1` to use built-in `URL` class to parse hostname instead. `Hawk.authenticate()` accepts `options` argument. If that contains `host` and `port`, those would be used instead of a call to `utils.parseHost()`.", 'packageVersion': '3.1.3', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'hawk', 'publishedDate': '2022-05-05T23:15:00Z', 'cvss': 7.5, 'status': 'fixed in 9.0.1'}, {'severity': 'medium', 'riskFactors': {'Medium severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2022-33987', 'link': 'https://github.com/advisories/GHSA-pfrx-2q88-qq97', 'description': 'The got package before 12.1.0 (also fixed in 11.8.5) for Node.js allows a redirect to a UNIX socket.', 'packageVersion': '6.7.1', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N', 'packageName': 'got', 'publishedDate': '2022-06-18T21:15:00Z', 'cvss': 5.3, 'status': 'fixed in 12.1.0'}, {'severity': 'medium', 'riskFactors': {'Medium severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2016-1000232', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2016-1000232', 'description': 'NodeJS Tough-Cookie version 2.2.2 contains a Regular Expression Parsing vulnerability in HTTP request Cookie Header parsing that can result in Denial of Service. This attack appear to be exploitable via Custom HTTP header passed by client. This vulnerability appears to have been fixed in 2.3.0.', 'packageVersion': '2.2.2', 'vector': 'CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L', 'packageName': 'tough-cookie', 'publishedDate': '2016-07-22T00:00:00Z', 'cvss': 5.3, 'status': ''}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2017-15010', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2017-15010', 'description': 'A ReDoS (regular expression denial of service) flaw was found in the tough-cookie module before 2.3.3 for Node.js. An attacker that is able to make an HTTP request using a specially crafted cookie may cause the application to consume an excessive amount of CPU.', 'packageVersion': '2.2.2', 'vector': 'CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'tough-cookie', 'publishedDate': '2017-10-04T01:29:00Z', 'cvss': 7.5, 'status': 'fixed in 2.3.3'}, {'severity': 'critical', 'riskFactors': {'Critical severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2017-16042', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2017-16042', 'description': 'Growl adds growl notification support to nodejs. Growl before 1.10.2 does not properly sanitize input before passing it to exec, allowing for arbitrary command execution.', 'packageVersion': '1.9.2', 'vector': 'CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H', 'packageName': 'growl', 'publishedDate': '2018-06-04T19:29:00Z', 'cvss': 9.8, 'status': 'fixed in 1.10.2'}, {'severity': 'medium', 'riskFactors': {'Has fix': {}, 'Medium severity': {}, 'DoS': {}}, 'cveId': 'PRISMA-2021-0013', 'link': '', 'description': 'marked package prior to 1.1.1 are vulnerable to  Regular Expression Denial of Service (ReDoS). The regex within src/rules.js file have multiple unused capture groups which could lead to a denial of service attack if user input is reachable.  Origin: https://github.com/markedjs/marked/commit/bd4f8c464befad2b304d51e33e89e567326e62e0', 'packageVersion': '0.3.9', 'vector': '', 'packageName': 'marked', 'publishedDate': '2021-01-14T10:29:35Z', 'cvss': 0, 'status': 'fixed in 1.1.1'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2022-21681', 'link': 'https://github.com/advisories/GHSA-5v2h-r2cx-5xgj', 'description': 'Marked is a markdown parser and compiler. Prior to version 4.0.10, the regular expression `inline.reflinkSearch` may cause catastrophic backtracking against some strings and lead to a denial of service (DoS). Anyone who runs untrusted markdown through a vulnerable version of marked and does not use a worker with a time limit may be affected. This issue is patched in version 4.0.10. As a workaround, avoid running untrusted markdown through marked or run marked on a worker thread and set a reasonable time limit to prevent draining resources.', 'packageVersion': '0.3.9', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'marked', 'publishedDate': '2022-01-14T17:15:00Z', 'cvss': 7.5, 'status': 'fixed in 4.0.10'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2022-21680', 'link': 'https://github.com/advisories/GHSA-rrrm-qjm4-v8hf', 'description': 'Marked is a markdown parser and compiler. Prior to version 4.0.10, the regular expression `block.def` may cause catastrophic backtracking against some strings and lead to a regular expression denial of service (ReDoS). Anyone who runs untrusted markdown through a vulnerable version of marked and does not use a worker with a time limit may be affected. This issue is patched in version 4.0.10. As a workaround, avoid running untrusted markdown through marked or run marked on a worker thread and set a reasonable time limit to prevent draining resources.', 'packageVersion': '0.3.9', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'marked', 'publishedDate': '2022-01-14T17:15:00Z', 'cvss': 7.5, 'status': 'fixed in 4.0.10'}, {'severity': 'critical', 'riskFactors': {'Critical severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2021-44906', 'link': 'https://github.com/advisories/GHSA-xvch-5gv4-984h', 'description': 'Minimist <=1.2.5 is vulnerable to Prototype Pollution via file index.js, function setKey() (lines 69-95).', 'packageVersion': '1.2.5', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H', 'packageName': 'minimist', 'publishedDate': '2022-03-17T16:15:00Z', 'cvss': 9.8, 'status': 'fixed in 1.2.6'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'DoS': {}}, 'cveId': 'PRISMA-2022-0230', 'link': 'https://github.com/mochajs/mocha/pull/4770', 'description': 'mocha packages from all versions are vulnerable to Regular Expression Denial of Service (ReDoS). clean() function is vulnerable to ReDoS attack due to the overlapped sub-patterns.', 'packageVersion': '2.5.3', 'vector': '', 'packageName': 'mocha', 'publishedDate': '2022-07-07T11:32:57Z', 'cvss': 7.5, 'status': 'open'}, {'severity': 'medium', 'riskFactors': {'Medium severity': {}, 'DoS': {}}, 'cveId': 'PRISMA-2022-0335', 'link': 'https://github.com/mochajs/mocha/commit/61b4b9209c2c64b32c8d48b1761c3b9384d411ea', 'description': 'mocha packages from all versions are vulnerable to Regular Expression Denial of Service (ReDoS). clean() function in utils.js is vulnerable to ReDoS with the regex: /^function(?:\\\\s*|\\\\s+[^(]*)\\\\([^)]*\\\\)\\\\s*\\\\{((?:.|\\n)*?)\\\\s*\\\\}$|^\\\\([^)]*\\\\', 'packageVersion': '2.5.3', 'vector': '', 'packageName': 'mocha', 'publishedDate': '2022-10-02T18:01:01Z', 'cvss': 5.3, 'status': 'open'}, {'severity': 'moderate', 'riskFactors': {'Medium severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2021-23362', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2021-23362', 'description': 'The package hosted-git-info before 3.0.8 are vulnerable to Regular Expression Denial of Service (ReDoS) via regular expression shortcutMatch in the fromUrl function in index.js. The affected regular expression exhibits polynomial worst-case time complexity.', 'packageVersion': '2.1.5', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L', 'packageName': 'hosted-git-info', 'publishedDate': '2021-03-23T17:15:00Z', 'cvss': 4, 'status': 'fixed in 2.8.9, 3.0.8'}, {'severity': 'high', 'riskFactors': {'Has fix': {}, 'High severity': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2018-7408', 'link': 'https://github.com/advisories/GHSA-ph34-pc88-72gc', 'description': 'An issue was discovered in an npm 5.7.0 2018-02-21 pre-release (marked as \\"next: 5.7.0\\" and therefore automatically installed by an \\"npm upgrade -g npm\\" command, and also announced in the vendor\\\'s blog without mention of pre-release status). It might allow local users to bypass intended filesystem access restrictions because ownerships of /etc and /usr directories are being changed unexpectedly, related to a \\"correctMkdir\\" issue.', 'packageVersion': '3.10.10', 'vector': 'CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H', 'packageName': 'npm', 'publishedDate': '2018-02-22T18:29:00Z', 'cvss': 7, 'status': 'fixed in 5.7.1'}, {'severity': 'moderate', 'riskFactors': {'Has fix': {}, 'Medium severity': {}}, 'cveId': 'CVE-2020-15095', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2020-15095', 'description': 'Versions of the npm CLI prior to 6.14.6 are vulnerable to an information exposure vulnerability through log files. The CLI supports URLs like \\"<protocol>://[<user>[:<password>]@]<hostname>[:<port>][:][/]<path>\\". The password value is not redacted and is printed to stdout and also to any generated log files.', 'packageVersion': '3.10.10', 'vector': 'CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:N/A:N', 'packageName': 'npm', 'publishedDate': '2020-07-07T19:15:00Z', 'cvss': 4, 'status': 'fixed in 6.14.6'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2019-16775', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2019-16775', 'description': "Versions of the npm CLI prior to 6.13.3 are vulnerable to an Arbitrary File Write. It is possible for packages to create symlinks to files outside of thenode_modules folder through the bin field upon installation. A properly constructed entry in the package.json bin field would allow a package publisher to create a symlink pointing to arbitrary files on a user\\'s system when the package is installed. This behavior is still possible through install scripts. This vulnerability bypasses a user using the --ignore-scripts install option.", 'packageVersion': '3.10.10', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N', 'packageName': 'npm', 'publishedDate': '2019-12-13T01:15:00Z', 'cvss': 7, 'status': 'fixed in 6.13.3'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2019-16776', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2019-16776', 'description': "Versions of the npm CLI prior to 6.13.3 are vulnerable to an Arbitrary File Write. It fails to prevent access to folders outside of the intended node_modules folder through the bin field. A properly constructed entry in the package.json bin field would allow a package publisher to modify and/or gain access to arbitrary files on a user\\'s system when the package is installed. This behavior is still possible through install scripts. This vulnerability bypasses a user using the --ignore-scripts install option.", 'packageVersion': '3.10.10', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N', 'packageName': 'npm', 'publishedDate': '2019-12-13T01:15:00Z', 'cvss': 7, 'status': 'fixed in 6.13.3'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2019-16777', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2019-16777', 'description': 'Versions of the npm CLI prior to 6.13.4 are vulnerable to an Arbitrary File Overwrite. It fails to prevent existing globally-installed binaries to be overwritten by other package installations. For example, if a package was installed globally and created a serve binary, any subsequent installs of packages that also create a serve binary would overwrite the previous serve binary. This behavior is still allowed in local installations and also through install scripts. This vulnerability bypasses a user using the --ignore-scripts install option.', 'packageVersion': '3.10.10', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N', 'packageName': 'npm', 'publishedDate': '2019-12-13T01:15:00Z', 'cvss': 7, 'status': 'fixed in 6.13.4'}, {'severity': 'high', 'riskFactors': {'Has fix': {}, 'High severity': {}, 'DoS': {}}, 'cveId': 'GHSA-mh5c-679w-hh4r', 'link': '', 'description': 'Versions of `mongodb` prior to 3.1.13 are vulnerable to Denial of Service. The package fails to properly catch an exception when a collection name is invalid and the DB does not exist, crashing the application.   ## Recommendation  Upgrade to version 3.1.13 or later.', 'packageVersion': '2.2.36', 'vector': '', 'packageName': 'mongodb', 'publishedDate': '2020-09-03T21:12:01Z', 'cvss': 7, 'status': 'fixed in 3.1.13'}, {'severity': 'critical', 'riskFactors': {'Critical severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2020-7788', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2020-7788', 'description': 'This affects the package ini before 1.3.6. If an attacker submits a malicious INI file to an application that parses it with ini.parse, they will pollute the prototype on the application. This can be exploited further depending on the context.', 'packageVersion': '1.3.4', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H', 'packageName': 'ini', 'publishedDate': '2020-12-11T11:15:00Z', 'cvss': 9.8, 'status': 'fixed in 1.3.6'}, {'severity': 'high', 'riskFactors': {'Has fix': {}, 'High severity': {}, 'DoS': {}}, 'cveId': 'PRISMA-2022-0039', 'link': 'https://github.com/isaacs/minimatch/commit/a8763f4388e51956be62dc6025cec1126beeb5e6', 'description': "minimatch package versions before 3.0.5 are vulnerable to Regular Expression Denial of Service (ReDoS). It\\'s possible to cause a denial of service when calling function braceExpand (The regex /\\\\{.*\\\\}/ is vulnerable and can be exploited).", 'packageVersion': '0.3.0', 'vector': '', 'packageName': 'minimatch', 'publishedDate': '2022-02-21T09:51:41Z', 'cvss': 7.5, 'status': 'fixed in 3.0.5'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2016-10540', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2016-10540', 'description': 'Minimatch is a minimal matching utility that works by converting glob expressions into JavaScript `RegExp` objects. The primary function, `minimatch(path, pattern)` in Minimatch 3.0.1 and earlier is vulnerable to ReDoS in the `pattern` parameter.', 'packageVersion': '0.3.0', 'vector': 'CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'minimatch', 'publishedDate': '2018-05-31T20:29:00Z', 'cvss': 7.5, 'status': ''}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2022-3517', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2022-3517', 'description': 'A vulnerability was found in the minimatch package. This flaw allows a Regular Expression Denial of Service (ReDoS) when calling the braceExpand function with specific arguments, resulting in a Denial of Service.', 'packageVersion': '0.3.0', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'minimatch', 'publishedDate': '2022-10-17T20:15:00Z', 'cvss': 7.5, 'status': 'fixed in 3.0.5'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2017-18077', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2017-18077', 'description': 'index.js in brace-expansion before 1.1.7 is vulnerable to Regular Expression Denial of Service (ReDoS) attacks, as demonstrated by an expand argument containing many comma characters.', 'packageVersion': '1.1.6', 'vector': 'CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'brace-expansion', 'publishedDate': '2018-01-27T12:29:00Z', 'cvss': 7, 'status': 'fixed in 1.1.7'}, {'severity': 'high', 'riskFactors': {'Has fix': {}, 'High severity': {}, 'DoS': {}}, 'cveId': 'PRISMA-2022-0039', 'link': 'https://github.com/isaacs/minimatch/commit/a8763f4388e51956be62dc6025cec1126beeb5e6', 'description': "minimatch package versions before 3.0.5 are vulnerable to Regular Expression Denial of Service (ReDoS). It\\'s possible to cause a denial of service when calling function braceExpand (The regex /\\\\{.*\\\\}/ is vulnerable and can be exploited).", 'packageVersion': '3.0.3', 'vector': '', 'packageName': 'minimatch', 'publishedDate': '2022-02-21T09:51:41Z', 'cvss': 7.5, 'status': 'fixed in 3.0.5'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2022-3517', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2022-3517', 'description': 'A vulnerability was found in the minimatch package. This flaw allows a Regular Expression Denial of Service (ReDoS) when calling the braceExpand function with specific arguments, resulting in a Denial of Service.', 'packageVersion': '3.0.3', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'minimatch', 'publishedDate': '2022-10-17T20:15:00Z', 'cvss': 7.5, 'status': 'fixed in 3.0.5'}, {'severity': 'low', 'riskFactors': {'Has fix': {}}, 'cveId': 'CVE-2017-18869', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2017-18869', 'description': 'A TOCTOU issue in the chownr package before 1.1.0 for Node.js 10.10 could allow a local attacker to trick it into descending into unintended directories via symlink attacks.', 'packageVersion': '1.0.1', 'vector': 'CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:N', 'packageName': 'chownr', 'publishedDate': '2020-06-15T15:15:00Z', 'cvss': 2.5, 'status': 'fixed in 1.1.0'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2019-13173', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2019-13173', 'description': "fstream before 1.0.12 is vulnerable to Arbitrary File Overwrite. Extracting tarballs containing a hardlink to a file that already exists in the system, and a file that matches the hardlink, will overwrite the system\\'s file with the contents of the extracted file. The fstream.DirWriter() function is vulnerable.", 'packageVersion': '1.0.10', 'vector': 'CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N', 'packageName': 'fstream', 'publishedDate': '2019-07-02T20:15:00Z', 'cvss': 7.5, 'status': 'fixed in 1.0.12'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2022-31129', 'link': 'https://github.com/advisories/GHSA-wc69-rhjr-hc9g', 'description': 'moment is a JavaScript date library for parsing, validating, manipulating, and formatting dates. Affected versions of moment were found to use an inefficient parsing algorithm. Specifically using string-to-date parsing in moment (more specifically rfc2822 parsing, which is tried by default) has quadratic (N^2) complexity on specific inputs. Users may notice a noticeable slowdown is observed with inputs above 10k characters. Users who pass user-provided strings without sanity length checks to moment constructor are vulnerable to (Re)DoS attacks. The problem is patched in 2.29.4, the patch can be applied to all affected versions with minimal tweaking. Users are advised to upgrade. Users unable to upgrade should consider limiting date lengths accepted from user input.', 'packageVersion': '2.24.0', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'moment', 'publishedDate': '2022-07-06T18:15:00Z', 'cvss': 7.5, 'status': 'fixed in 2.29.4'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2022-24785', 'link': 'https://github.com/advisories/GHSA-8hfj-j24r-96c4', 'description': 'Moment.js is a JavaScript date library for parsing, validating, manipulating, and formatting dates. A path traversal vulnerability impacts npm (server) users of Moment.js between versions 1.0.1 and 2.29.1, especially if a user-provided locale string is directly used to switch moment locale. This problem is patched in 2.29.2, and the patch can be applied to all affected versions. As a workaround, sanitize the user-provided locale name before passing it to Moment.js.', 'packageVersion': '2.24.0', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N', 'packageName': 'moment', 'publishedDate': '2022-04-04T17:15:00Z', 'cvss': 7.5, 'status': 'fixed in 2.29.2'}, {'severity': 'medium', 'riskFactors': {'Has fix': {}, 'Medium severity': {}}, 'cveId': 'PRISMA-2022-0087', 'link': 'https://github.com/ljharb/qs/issues/200', 'description': "qs package versions before 6.3.1 are vulnerable to Prototype Pollution. It\\'s a bypass for CVE-2017-1000048, that only fixed ]=toString, but not fixed  [=toString. So it is possible to override prototype properties such as toString() for a nested object which exceeds the depth limit even when allowPrototypes is set to false.", 'packageVersion': '6.2.1', 'vector': '', 'packageName': 'qs', 'publishedDate': '2022-03-17T09:41:42Z', 'cvss': 5.9, 'status': 'fixed in 6.3.1'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2022-24999', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2022-24999', 'description': 'qs before 6.10.3, as used in Express before 4.17.3 and other products, allows attackers to cause a Node process hang for an Express application because an __ proto__ key can be used. In many typical Express use cases, an unauthenticated remote attacker can place the attack payload in the query string of the URL that is used to visit the application, such as a[__proto__]=b&a[__proto__]&a[length]=100000000. The fix was backported to qs 6.9.7, 6.8.3, 6.7.3, 6.6.1, 6.5.3, 6.4.1, 6.3.3, and 6.2.4 (and therefore Express 4.17.3, which has \\"deps: qs@6.9.7\\" in its release description, is not vulnerable).', 'packageVersion': '6.2.1', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'qs', 'publishedDate': '2022-11-26T22:15:00Z', 'cvss': 7.5, 'status': 'fixed in 6.10.3'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2017-1000048', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2017-1000048', 'description': "the web framework using ljharb\\'s qs module older than v6.3.2, v6.2.3, v6.1.2, and v6.0.4 is vulnerable to a DoS. A malicious user can send a evil request to cause the web framework crash.", 'packageVersion': '6.2.1', 'vector': 'CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'qs', 'publishedDate': '2017-03-01T00:00:00Z', 'cvss': 7, 'status': 'fixed in 6.3.2, 6.2.3, 6.1.2, 6.0.4'}, {'severity': 'medium', 'riskFactors': {'Medium severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2018-1107', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2018-1107', 'description': 'It was discovered that the is-my-json-valid JavaScript library used an inefficient regular expression to validate JSON fields defined to have email format. A specially crafted JSON file could cause it to consume an excessive amount of CPU time when validated.', 'packageVersion': '2.15.0', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L', 'packageName': 'is-my-json-valid', 'publishedDate': '2018-02-16T00:00:00Z', 'cvss': 5.3, 'status': 'fixed in 2.17.2, 1.4.1'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2016-2537', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2016-2537', 'description': "The is-my-json-valid package before 2.12.4 for Node.js has an incorrect exports[\\'utc-millisec\\'] regular expression, which allows remote attackers to cause a denial of service (blocked event loop) via a crafted string.", 'packageVersion': '2.15.0', 'vector': 'CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'is-my-json-valid', 'publishedDate': '2016-02-23T05:59:00Z', 'cvss': 7, 'status': 'fixed in 1.4.1, 2.17.2'}, {'severity': 'moderate', 'riskFactors': {'Medium severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2020-8244', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2020-8244', 'description': 'A buffer over-read vulnerability exists in bl <4.0.3, <3.0.1, <2.2.1, and <1.2.3 which could allow an attacker to supply user input (even typed) that if it ends up in consume() argument and can become negative, the BufferList state can be corrupted, tricking it into exposing uninitialized memory via regular .slice() calls.', 'packageVersion': '1.1.2', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L', 'packageName': 'bl', 'publishedDate': '2020-08-30T15:15:00Z', 'cvss': 4, 'status': 'fixed in 2.2.1, 1.2.3, 4.0.3, 3.0.1'}, {'severity': 'moderate', 'riskFactors': {'Attack vector: network': {}, 'Has fix': {}, 'Medium severity': {}}, 'cveId': 'CVE-2018-21270', 'link': 'https://github.com/advisories/GHSA-mf6x-7mm4-x2g7', 'description': 'Versions less than 0.0.6 of the Node.js stringstream module are vulnerable to an out-of-bounds read because of allocation of uninitialized buffers when a number is passed in the input stream (when using Node.js 4.x).', 'packageVersion': '0.0.5', 'vector': 'CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:H', 'packageName': 'stringstream', 'publishedDate': '2020-12-03T21:15:00Z', 'cvss': 4, 'status': 'fixed in 0.0.6'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2020-7754', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2020-7754', 'description': 'This affects the package npm-user-validate before 1.0.1. The regex that validates user emails took exponentially longer to process long input strings beginning with @ characters.', 'packageVersion': '0.1.5', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'npm-user-validate', 'publishedDate': '2020-10-16T00:00:00Z', 'cvss': 7.5, 'status': 'fixed in 1.0.1'}, {'severity': 'low', 'riskFactors': {'Has fix': {}, 'DoS': {}}, 'cveId': 'GHSA-xgh6-85xh-479p', 'link': '', 'description': '`npm-user-validate` before version `1.0.1` is vulnerable to a Regular Expression Denial of Service (REDos). The regex that validates user emails took exponentially longer to process long input strings beginning with `@` characters.  ### Impact The issue affects the `email` function. If you use this function to process arbitrary user input with no character limit the application may be susceptible to Denial of Service.  ### Patches The issue is patched in version 1.0.1 by improving the regular expression used and also enforcing a 254 character limit.  ### Workarounds Restrict the character length to a reasonable degree before passing a value to `.emal()`; Also, consider doing a more rigorous sanitizing/validation beforehand.', 'packageVersion': '0.1.5', 'vector': '', 'packageName': 'npm-user-validate', 'publishedDate': '2020-10-16T18:56:26Z', 'cvss': 1, 'status': 'fixed in 1.0.1'}, {'severity': 'medium', 'riskFactors': {'Medium severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2018-1109', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2018-1109', 'description': 'A vulnerability was found in Braces versions prior to 2.3.1. Affected versions of this package are vulnerable to Regular Expression Denial of Service (ReDoS) attacks.', 'packageVersion': '1.8.5', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L', 'packageName': 'braces', 'publishedDate': '2021-03-30T02:15:00Z', 'cvss': 5.3, 'status': 'fixed in 2.3.1'}, {'severity': 'low', 'riskFactors': {'Has fix': {}, 'DoS': {}}, 'cveId': 'GHSA-g95f-p29q-9xw4', 'link': '', 'description': 'Versions of `braces` prior to 2.3.1 are vulnerable to Regular Expression Denial of Service (ReDoS). Untrusted input may cause catastrophic backtracking while matching regular expressions. This can cause the application to be unresponsive leading to Denial of Service.   ## Recommendation  Upgrade to version 2.3.1 or higher.', 'packageVersion': '1.8.5', 'vector': '', 'packageName': 'braces', 'publishedDate': '2019-06-06T15:30:30Z', 'cvss': 1, 'status': 'fixed in 2.3.1'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2021-37713', 'link': 'https://github.com/advisories/GHSA-5955-9wpr-37jh', 'description': 'The npm package \\"tar\\" (aka node-tar) before versions 4.4.18, 5.0.10, and 6.1.9 has an arbitrary file creation/overwrite and arbitrary code execution vulnerability. node-tar aims to guarantee that any file whose location would be outside of the extraction target directory is not extracted. This is, in part, accomplished by sanitizing absolute paths of entries within the archive, skipping archive entries that contain `..` path portions, and resolving the sanitized paths against the extraction target directory. This logic was insufficient on Windows systems when extracting tar files that contained a path that was not an absolute path, but specified a drive letter different from the extraction target, such as `C:some\\\\path`. If the drive letter does not match the extraction target, for example `D:\\\\extraction\\\\dir`, then the result of `path.resolve(extractionDirectory, entryPath)` would resolve against the current working directory on the `C:` drive, rather than the extraction target directory. Additionally, a `..` portion of the path could occur immediately after the drive letter, such as `C:../foo`, and was not properly sanitized by the logic that checked for `..` within the normalized and split portions of the path. This only affects users of `node-tar` on Windows systems. These issues were addressed in releases 4.4.18, 5.0.10 and 6.1.9. The v3 branch of node-tar has been deprecate', 'packageVersion': '2.2.1', 'vector': 'CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H', 'packageName': 'tar', 'publishedDate': '2021-08-31T17:15:00Z', 'cvss': 7, 'status': 'fixed in 6.1.9, 5.0.10, 4.4.18'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2021-37712', 'link': 'https://github.com/advisories/GHSA-qq89-hq3f-393p', 'description': 'The npm package \\"tar\\" (aka node-tar) before versions 4.4.18, 5.0.10, and 6.1.9 has an arbitrary file creation/overwrite and arbitrary code execution vulnerability. node-tar aims to guarantee that any file whose location would be modified by a symbolic link is not extracted. This is, in part, achieved by ensuring that extracted directories are not symlinks. Additionally, in order to prevent unnecessary stat calls to determine whether a given path is a directory, paths are cached when directories are created. This logic was insufficient when extracting tar files that contained both a directory and a symlink with names containing unicode values that normalized to the same value. Additionally, on Windows systems, long path portions would resolve to the same file system entities as their 8.3 \\"short path\\" counterparts. A specially crafted tar archive could thus include a directory with one form of the path, followed by a symbolic link with a different string that resolves to the same file system entity, followed by a file using the first form. By first creating a directory, and then replacing that directory with a symlink that had a different apparent name that resolved to the same entry in the filesystem, it was thus possible to bypass node-tar symlink checks on directories, essentially allowing an untrusted tar file to symlink into an arbitrary location and subsequently extracting ', 'packageVersion': '2.2.1', 'vector': 'CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H', 'packageName': 'tar', 'publishedDate': '2021-08-31T17:15:00Z', 'cvss': 7, 'status': 'fixed in 6.1.9, 5.0.10, 4.4.18'}, {'severity': 'low', 'riskFactors': {'Has fix': {}, 'DoS': {}}, 'cveId': 'PRISMA-2021-0096', 'link': 'https://github.com/npm/node-tar/commit/06cbde5935aa7643f578f874de84a7da2a74fe3a', 'description': 'tar package versions before 6.1.4 are vulnerable to Regular Expression Denial of Service (ReDoS). When stripping the trailing slash from `files` arguments, we were using `f.replace(/\\\\/+$/, \\\'\\\')`, which can get exponentially slow when `f` contains many `/` characters. This is \\"\\"unlikely but theoretically possible\\"\\" because it requires that the user is passing untrusted input into the `tar.extract()` or `tar.list()` array of entries to parse/extract, which would be quite unusual.', 'packageVersion': '2.2.1', 'vector': '', 'packageName': 'tar', 'publishedDate': '2021-08-30T08:44:48Z', 'cvss': 3.5, 'status': 'fixed in 6.1.4'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2021-37701', 'link': 'https://github.com/advisories/GHSA-9r2w-394v-53qc', 'description': 'The npm package \\"tar\\" (aka node-tar) before versions 4.4.16, 5.0.8, and 6.1.7 has an arbitrary file creation/overwrite and arbitrary code execution vulnerability. node-tar aims to guarantee that any file whose location would be modified by a symbolic link is not extracted. This is, in part, achieved by ensuring that extracted directories are not symlinks. Additionally, in order to prevent unnecessary stat calls to determine whether a given path is a directory, paths are cached when directories are created. This logic was insufficient when extracting tar files that contained both a directory and a symlink with the same name as the directory, where the symlink and directory names in the archive entry used backslashes as a path separator on posix systems. The cache checking logic used both `\\\\` and `/` characters as path separators, however `\\\\` is a valid filename character on posix systems. By first creating a directory, and then replacing that directory with a symlink, it was thus possible to bypass node-tar symlink checks on directories, essentially allowing an untrusted tar file to symlink into an arbitrary location and subsequently extracting arbitrary files into that location, thus allowing arbitrary file creation and overwrite. Additionally, a similar confusion could arise on case-insensitive filesystems. If a tar archive contained a directory at `FOO`, followed by a symboli', 'packageVersion': '2.2.1', 'vector': 'CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H', 'packageName': 'tar', 'publishedDate': '2021-08-31T17:15:00Z', 'cvss': 8.6, 'status': 'fixed in 6.1.7, 5.0.8, 4.4.16'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2021-32804', 'link': 'https://github.com/advisories/GHSA-3jfq-g458-7qm9', 'description': 'The npm package \\"tar\\" (aka node-tar) before versions 6.1.1, 5.0.6, 4.4.14, and 3.3.2 has a arbitrary File Creation/Overwrite vulnerability due to insufficient absolute path sanitization. node-tar aims to prevent extraction of absolute file paths by turning absolute paths into relative paths when the `preservePaths` flag is not set to `true`. This is achieved by stripping the absolute path root from any absolute file paths contained in a tar file. For example `/home/user/.bashrc` would turn into `home/user/.bashrc`. This logic was insufficient when file paths contained repeated path roots such as `////home/user/.bashrc`. `node-tar` would only strip a single path root from such paths. When given an absolute file path with repeating path roots, the resulting path (e.g. `///home/user/.bashrc`) would still resolve to an absolute path, thus allowing arbitrary file creation and overwrite. This issue was addressed in releases 3.2.2, 4.4.14, 5.0.6 and 6.1.1. Users may work around this vulnerability without upgrading by creating a custom `onentry` method which sanitizes the `entry.path` or a `filter` method which removes entries with absolute paths. See referenced GitHub Advisory for details. Be aware of CVE-2021-32803 which fixes a similar bug in later versions of tar.', 'packageVersion': '2.2.1', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H', 'packageName': 'tar', 'publishedDate': '2021-08-03T19:15:00Z', 'cvss': 8.1, 'status': 'fixed in 6.1.1, 5.0.6, 4.4.14,...'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2021-32803', 'link': 'https://github.com/advisories/GHSA-r628-mhmh-qjhw', 'description': 'The npm package \\"tar\\" (aka node-tar) before versions 6.1.2, 5.0.7, 4.4.15, and 3.2.3 has an arbitrary File Creation/Overwrite vulnerability via insufficient symlink protection. `node-tar` aims to guarantee that any file whose location would be modified by a symbolic link is not extracted. This is, in part, achieved by ensuring that extracted directories are not symlinks. Additionally, in order to prevent unnecessary `stat` calls to determine whether a given path is a directory, paths are cached when directories are created. This logic was insufficient when extracting tar files that contained both a directory and a symlink with the same name as the directory. This order of operations resulted in the directory being created and added to the `node-tar` directory cache. When a directory is present in the directory cache, subsequent calls to mkdir for that directory are skipped. However, this is also where `node-tar` checks for symlinks occur. By first creating a directory, and then replacing that directory with a symlink, it was thus possible to bypass `node-tar` symlink checks on directories, essentially allowing an untrusted tar file to symlink into an arbitrary location and subsequently extracting arbitrary files into that location, thus allowing arbitrary file creation and overwrite. This issue was addressed in releases 3.2.3, 4.4.15, 5.0.7 and 6.1.2.', 'packageVersion': '2.2.1', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H', 'packageName': 'tar', 'publishedDate': '2021-08-03T19:15:00Z', 'cvss': 8.1, 'status': 'fixed in 6.1.2, 5.0.7, 4.4.15,...'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2018-20834', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2018-20834', 'description': 'A vulnerability was found in node-tar before version 4.4.2 (excluding version 2.2.2). An Arbitrary File Overwrite issue exists when extracting a tarball containing a hardlink to a file that already exists on the system, in conjunction with a later plain file with the same name as the hardlink. This plain file content replaces the existing file content. A patch has been applied to node-tar v2.2.2', 'packageVersion': '2.2.1', 'vector': 'CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N', 'packageName': 'tar', 'publishedDate': '2019-04-30T19:29:00Z', 'cvss': 7, 'status': 'fixed in 4.4.2, 2.2.2'}, {'severity': 'critical', 'riskFactors': {'Critical severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2021-3918', 'link': 'https://github.com/advisories/GHSA-896r-f27r-55mw', 'description': "json-schema is vulnerable to Improperly Controlled Modification of Object Prototype Attributes (\\'Prototype Pollution\\')", 'packageVersion': '0.2.3', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H', 'packageName': 'json-schema', 'publishedDate': '2021-11-13T09:15:00Z', 'cvss': 9, 'status': 'fixed in 0.4.0'}, {'severity': 'critical', 'riskFactors': {'Critical severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2021-23807', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2021-23807', 'description': 'This affects the package jsonpointer before 5.0.0. A type confusion vulnerability can lead to a bypass of a previous Prototype Pollution fix when the pointer components are arrays.', 'packageVersion': '4.0.0', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H', 'packageName': 'jsonpointer', 'publishedDate': '2021-08-31T00:00:00Z', 'cvss': 9.8, 'status': 'fixed in 5.0.0'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2017-15010', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2017-15010', 'description': 'A ReDoS (regular expression denial of service) flaw was found in the tough-cookie module before 2.3.3 for Node.js. An attacker that is able to make an HTTP request using a specially crafted cookie may cause the application to consume an excessive amount of CPU.', 'packageVersion': '2.3.1', 'vector': 'CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'tough-cookie', 'publishedDate': '2017-10-04T01:29:00Z', 'cvss': 7.5, 'status': 'fixed in 2.3.3'}, {'severity': 'critical', 'riskFactors': {'Critical severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2018-16492', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2018-16492', 'description': 'A prototype pollution vulnerability was found in module extend <2.0.2, ~<3.0.2 that allows an attacker to inject arbitrary properties onto Object.prototype.', 'packageVersion': '3.0.0', 'vector': 'CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H', 'packageName': 'extend', 'publishedDate': '2019-02-01T18:29:00Z', 'cvss': 9.8, 'status': 'fixed in 3.0.2, 2.0.2'}, {'severity': 'medium', 'riskFactors': {'Has fix': {}, 'Medium severity': {}, 'DoS': {}}, 'cveId': 'PRISMA-2021-0169', 'link': 'https://github.com/mishoo/UglifyJS/pull/5134', 'description': 'uglify-js package versions before 3.14.3 are vulnerable to Regular Expression Denial of Service (ReDoS) via minify() function that uses vulnerable regex.', 'packageVersion': '2.7.0', 'vector': '', 'packageName': 'uglify-js', 'publishedDate': '2021-12-23T10:05:50Z', 'cvss': 5.3, 'status': 'fixed in 3.14.3'}, {'severity': 'medium', 'riskFactors': {'Has fix': {}, 'Medium severity': {}}, 'cveId': 'PRISMA-2022-0005', 'link': 'https://github.com/istanbuljs/istanbuljs/commit/4eceb9eb8b3169b882d74ecc526fb5837ebc6205', 'description': 'istanbul-reports package versions before 3.1.3 are vulnerable to Reverse Tabnabbing. Tabnabbing - \\"it\\\'s the capacity to act on parent page\\\'s content or location from a newly opened page via the backlink exposed by the opener javascript object instance.\\" This vulnerability usually manifests when either The \\"target\\" attribute is used to specify the target location in an anchor tag to open 3rd party URL/resource(s) without including the attribute rel=\\"noopener,noreferrer \\" in the anchor tag.', 'packageVersion': '1.0.0-alpha.8', 'vector': '', 'packageName': 'istanbul-reports', 'publishedDate': '2022-01-25T11:13:51Z', 'cvss': 5.3, 'status': 'fixed in 3.1.3'}, {'severity': 'medium', 'riskFactors': {'Medium severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2017-16028', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2017-16028', 'description': 'react-native-meteor-oauth is a library for Oauth2 login to a Meteor server in React Native. The oauth Random Token is generated using a non-cryptographically strong RNG (Math.random()).', 'packageVersion': '1.1.5', 'vector': 'CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N', 'packageName': 'randomatic', 'publishedDate': '2018-06-04T19:29:00Z', 'cvss': 5.3, 'status': 'fixed in 3.0.0'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2019-20922', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2019-20922', 'description': 'Handlebars before 4.4.5 allows Regular Expression Denial of Service (ReDoS) because of eager matching. The parser may be forced into an endless loop while processing crafted templates. This may allow attackers to exhaust system resources.', 'packageVersion': '4.0.5', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'handlebars', 'publishedDate': '2020-09-30T18:15:00Z', 'cvss': 7.5, 'status': 'fixed in 4.4.5'}, {'severity': 'high', 'riskFactors': {'Attack vector: network': {}, 'Has fix': {}, 'High severity': {}}, 'cveId': 'CVE-2019-20920', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2019-20920', 'description': "Handlebars before 3.0.8 and 4.x before 4.5.3 is vulnerable to Arbitrary Code Execution. The lookup helper fails to properly validate templates, allowing attackers to submit templates that execute arbitrary JavaScript. This can be used to run arbitrary code on a server processing Handlebars templates or in a victim\\'s browser (effectively serving as XSS).", 'packageVersion': '4.0.5', 'vector': 'CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:L/A:L', 'packageName': 'handlebars', 'publishedDate': '2020-09-30T18:15:00Z', 'cvss': 8.1, 'status': 'fixed in 4.5.3, 3.0.8'}, {'severity': 'critical', 'riskFactors': {'Critical severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}, 'Remote execution': {}}, 'cveId': 'CVE-2021-23369', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2021-23369', 'description': 'The package handlebars before 4.7.7 are vulnerable to Remote Code Execution (RCE) when selecting certain compiling options to compile templates coming from an untrusted source.', 'packageVersion': '4.0.5', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H', 'packageName': 'handlebars', 'publishedDate': '2021-05-06T15:57:44Z', 'cvss': 9.8, 'status': 'fixed in 4.7.7'}, {'severity': 'critical', 'riskFactors': {'Critical severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2021-23383', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2021-23383', 'description': 'The package handlebars before 4.7.7 are vulnerable to Prototype Pollution when selecting certain compiling options to compile templates coming from an untrusted source.', 'packageVersion': '4.0.5', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H', 'packageName': 'handlebars', 'publishedDate': '2021-05-04T09:15:00Z', 'cvss': 9.8, 'status': 'fixed in 4.7.7'}, {'severity': 'high', 'riskFactors': {'Has fix': {}, 'High severity': {}}, 'cveId': 'GHSA-2cf5-4w76-r9qv', 'link': '', 'description': 'Versions of `handlebars` prior to 3.0.8 or 4.5.2 are vulnerable to Arbitrary Code Execution. The package\\\'s lookup helper fails to properly validate templates, allowing attackers to submit templates that execute arbitrary JavaScript in the system. It can be used to run arbitrary code in a server processing Handlebars templates or on a victim\\\'s browser (effectively serving as Cross-Site Scripting).  The following template can be used to demonstrate the vulnerability:   ```{{#with \\"constructor\\"}} \t{{#with split as |a|}} \t\t{{pop (push \\"alert(\\\'Vulnerable Handlebars JS\\\');\\")}} \t\t{{#with (concat (lookup join (slice 0 1)))}} \t\t\t{{#each (slice 2 3)}} \t\t\t\t{{#with (apply 0 a)}} \t\t\t\t\t{{.}} \t\t\t\t{{/with}} \t\t\t{{/each}} \t\t{{/with}} \t{{/with}} {{/with}}```   ## Recommendation  Upgrade to version 3.0.8, 4.5.2 or later.', 'packageVersion': '4.0.5', 'vector': '', 'packageName': 'handlebars', 'publishedDate': '2020-09-04T14:57:38Z', 'cvss': 7, 'status': 'fixed in 4.5.2, 3.0.8'}, {'severity': 'moderate', 'riskFactors': {'Has fix': {}, 'Medium severity': {}, 'DoS': {}}, 'cveId': 'GHSA-f52g-6jhx-586p', 'link': '', 'description': "Affected versions of `handlebars` are vulnerable to Denial of Service. The package\\'s parser may be forced into an endless loop while processing specially-crafted templates. This may allow attackers to exhaust system resources leading to Denial of Service.   ## Recommendation  Upgrade to version 4.4.5 or later.", 'packageVersion': '4.0.5', 'vector': '', 'packageName': 'handlebars', 'publishedDate': '2020-09-03T23:20:12Z', 'cvss': 4, 'status': 'fixed in 4.4.5'}, {'severity': 'high', 'riskFactors': {'Has fix': {}, 'High severity': {}}, 'cveId': 'GHSA-g9r4-xpmj-mj65', 'link': '', 'description': 'Versions of `handlebars` prior to 3.0.8 or 4.5.3 are vulnerable to prototype pollution. It is possible to add or modify properties to the Object prototype through a malicious template. This may allow attackers to crash the application or execute Arbitrary Code in specific conditions.   ## Recommendation  Upgrade to version 3.0.8, 4.5.3 or later.', 'packageVersion': '4.0.5', 'vector': '', 'packageName': 'handlebars', 'publishedDate': '2020-09-04T15:06:32Z', 'cvss': 7, 'status': 'fixed in 4.5.3, 3.0.8'}, {'severity': 'high', 'riskFactors': {'Has fix': {}, 'High severity': {}}, 'cveId': 'GHSA-q2c6-c6pm-g3gh', 'link': '', 'description': "Versions of `handlebars` prior to 3.0.8 or 4.5.3 are vulnerable to Arbitrary Code Execution. The package\\'s lookup helper fails to properly validate templates, allowing attackers to submit templates that execute arbitrary JavaScript in the system. It is due to an incomplete fix for a [previous issue](https://www.npmjs.com/advisories/1316). This vulnerability can be used to run arbitrary code in a server processing Handlebars templates or on a victim\\'s browser (effectively serving as Cross-Site Scripting).   ## Recommendation  Upgrade to version 3.0.8, 4.5.3 or later.", 'packageVersion': '4.0.5', 'vector': '', 'packageName': 'handlebars', 'publishedDate': '2020-09-04T15:07:38Z', 'cvss': 7, 'status': 'fixed in 4.5.3, 3.0.8'}, {'severity': 'high', 'riskFactors': {'Has fix': {}, 'High severity': {}}, 'cveId': 'GHSA-q42p-pg8m-cqh6', 'link': '', 'description': "Versions of `handlebars` prior to 4.0.14 are vulnerable to Prototype Pollution. Templates may alter an Objects\\' prototype, thus allowing an attacker to execute arbitrary code on the server.   ## Recommendation  For handlebars 4.1.x upgrade to 4.1.2 or later. For handlebars 4.0.x upgrade to 4.0.14 or later.", 'packageVersion': '4.0.5', 'vector': '', 'packageName': 'handlebars', 'publishedDate': '2019-06-05T14:07:48Z', 'cvss': 7, 'status': 'fixed in 3.0.7, 4.0.14, 4.1.2'}, {'severity': 'critical', 'riskFactors': {'Critical severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Remote execution': {}}, 'cveId': 'CVE-2019-19919', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2019-19919', 'description': "Versions of handlebars prior to 4.3.0 are vulnerable to Prototype Pollution leading to Remote Code Execution. Templates may alter an Object\\'s __proto__ and __defineGetter__ properties, which may allow an attacker to execute arbitrary code through crafted payloads.", 'packageVersion': '4.0.5', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H', 'packageName': 'handlebars', 'publishedDate': '2019-12-20T23:15:00Z', 'cvss': 9, 'status': 'fixed in 4.3.0'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2021-23343', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2021-23343', 'description': 'All versions of package path-parse are vulnerable to Regular Expression Denial of Service (ReDoS) via splitDeviceRe, splitTailRe, and splitPathRe regular expressions. ReDoS exhibits polynomial worst-case time complexity.', 'packageVersion': '1.0.5', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'path-parse', 'publishedDate': '2021-05-04T00:00:00Z', 'cvss': 7.5, 'status': 'fixed in 1.0.7'}, {'severity': 'critical', 'riskFactors': {'Critical severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2019-10744', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2019-10744', 'description': 'Versions of lodash lower than 4.17.12 are vulnerable to Prototype Pollution. The function defaultsDeep could be tricked into adding or modifying properties of Object.prototype using a constructor payload.', 'packageVersion': '4.13.1', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H', 'packageName': 'lodash', 'publishedDate': '2019-07-26T00:15:00Z', 'cvss': 9.1, 'status': 'fixed in 4.17.12'}, {'severity': 'high', 'riskFactors': {'Attack vector: network': {}, 'Has fix': {}, 'High severity': {}}, 'cveId': 'CVE-2020-8203', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2020-8203', 'description': 'Prototype pollution attack when using _.zipObjectDeep in lodash before 4.17.20.', 'packageVersion': '4.13.1', 'vector': 'CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H', 'packageName': 'lodash', 'publishedDate': '2020-07-15T17:15:00Z', 'cvss': 7.4, 'status': 'fixed in 4.17.20'}, {'severity': 'medium', 'riskFactors': {'Attack vector: network': {}, 'Has fix': {}, 'Medium severity': {}}, 'cveId': 'CVE-2018-16487', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2018-16487', 'description': 'A prototype pollution vulnerability was found in lodash <4.17.11 where the functions merge, mergeWith, and defaultsDeep can be tricked into adding or modifying properties of Object.prototype.', 'packageVersion': '4.13.1', 'vector': 'CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L', 'packageName': 'lodash', 'publishedDate': '2019-02-01T18:29:00Z', 'cvss': 5.6, 'status': 'fixed in 4.17.11'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2021-23337', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2021-23337', 'description': 'Lodash versions prior to 4.17.21 are vulnerable to Command Injection via the template function.', 'packageVersion': '4.13.1', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H', 'packageName': 'lodash', 'publishedDate': '2021-02-15T13:15:00Z', 'cvss': 7.2, 'status': 'fixed in 4.17.21'}, {'severity': 'medium', 'riskFactors': {'Medium severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2019-1010266', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2019-1010266', 'description': 'lodash prior to 4.17.11 is affected by: CWE-400: Uncontrolled Resource Consumption. The impact is: Denial of service. The component is: Date handler. The attack vector is: Attacker provides very long strings, which the library attempts to match using a regular expression. The fixed version is: 4.17.11.', 'packageVersion': '4.13.1', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'lodash', 'publishedDate': '2019-07-17T21:15:00Z', 'cvss': 6.5, 'status': 'fixed in 4.17.11'}, {'severity': 'medium', 'riskFactors': {'Medium severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2020-28500', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2020-28500', 'description': 'Lodash versions prior to 4.17.21 are vulnerable to Regular Expression Denial of Service (ReDoS) via the toNumber, trim and trimEnd functions.', 'packageVersion': '4.13.1', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L', 'packageName': 'lodash', 'publishedDate': '2021-02-15T11:15:00Z', 'cvss': 5.3, 'status': 'fixed in 4.17.21'}, {'severity': 'medium', 'riskFactors': {'Medium severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2018-3721', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2018-3721', 'description': 'lodash node module before 4.17.5 suffers from a Modification of Assumed-Immutable Data (MAID) vulnerability via defaultsDeep, merge, and mergeWith functions, which allows a malicious user to modify the prototype of \\"Object\\" via __proto__, causing the addition or modification of an existing property that will exist on all objects.', 'packageVersion': '4.13.1', 'vector': 'CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N', 'packageName': 'lodash', 'publishedDate': '2018-06-07T02:29:00Z', 'cvss': 6.5, 'status': 'fixed in 4.17.5'}, {'severity': 'high', 'riskFactors': {'Has fix': {}, 'High severity': {}, 'DoS': {}}, 'cveId': 'PRISMA-2022-0039', 'link': 'https://github.com/isaacs/minimatch/commit/a8763f4388e51956be62dc6025cec1126beeb5e6', 'description': "minimatch package versions before 3.0.5 are vulnerable to Regular Expression Denial of Service (ReDoS). It\\'s possible to cause a denial of service when calling function braceExpand (The regex /\\\\{.*\\\\}/ is vulnerable and can be exploited).", 'packageVersion': '3.0.2', 'vector': '', 'packageName': 'minimatch', 'publishedDate': '2022-02-21T09:51:41Z', 'cvss': 7.5, 'status': 'fixed in 3.0.5'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2022-3517', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2022-3517', 'description': 'A vulnerability was found in the minimatch package. This flaw allows a Regular Expression Denial of Service (ReDoS) when calling the braceExpand function with specific arguments, resulting in a Denial of Service.', 'packageVersion': '3.0.2', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'minimatch', 'publishedDate': '2022-10-17T20:15:00Z', 'cvss': 7.5, 'status': 'fixed in 3.0.5'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2020-28469', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2020-28469', 'description': 'This affects the package glob-parent before 5.1.2. The enclosure regex used to check for strings ending in enclosure containing path separator.', 'packageVersion': '2.0.0', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'glob-parent', 'publishedDate': '2021-06-03T16:15:00Z', 'cvss': 7.5, 'status': 'fixed in 5.1.2'}, {'severity': 'medium', 'riskFactors': {'Has fix': {}, 'Medium severity': {}, 'DoS': {}}, 'cveId': 'PRISMA-2021-0154', 'link': 'https://github.com/ramda/ramda/pull/3212/commits/94d057032c9b3ecf26d9842fbb12c981bda29f4b', 'description': 'ramda package versions before 0.27.2 are vulnerable to Regular Expression Denial of Service (ReDoS). Crafted input to the trim function may cause an application to consume an excessive amount of CPU.', 'packageVersion': '0.24.1', 'vector': '', 'packageName': 'ramda', 'publishedDate': '2021-11-17T09:17:03Z', 'cvss': 5.3, 'status': 'fixed in 0.27.2'}, {'severity': 'medium', 'riskFactors': {'Has fix': {}, 'Medium severity': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2020-7608', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2020-7608', 'description': 'yargs-parser could be tricked into adding or modifying properties of Object.prototype using a \\"__proto__\\" payload.', 'packageVersion': '2.4.1', 'vector': 'CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L', 'packageName': 'yargs-parser', 'publishedDate': '2020-03-16T20:15:00Z', 'cvss': 5.3, 'status': 'fixed in 5.0.1'}, {'severity': 'moderate', 'riskFactors': {'Has fix': {}, 'Medium severity': {}}, 'cveId': 'GHSA-64g7-mvw6-v9qj', 'link': 'https://github.com/advisories/GHSA-64g7-mvw6-v9qj', 'description': '### Impact Output from the synchronous version of `shell.exec()` may be visible to other users on the same system. You may be affected if you execute `shell.exec()` in multi-user Mac, Linux, or WSL environments, or if you execute `shell.exec()` as the root user.  Other shelljs functions (including the asynchronous version of `shell.exec()`) are not impacted.  ### Patches Patched in shelljs 0.8.5  ### Workarounds Recommended action is to upgrade to 0.8.5.  ### References https://huntr.dev/bounties/50996581-c08e-4eed-a90e-c0bac082679c/  ### For more information If you have any questions or comments about this advisory: * Ask at https://github.com/shelljs/shelljs/issues/1058 * Open an issue at https://github.com/shelljs/shelljs/issues/new ', 'packageVersion': '0.3.0', 'vector': '', 'packageName': 'shelljs', 'publishedDate': '2022-01-14T21:09:50Z', 'cvss': 4, 'status': 'fixed in 0.8.5'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2022-0144', 'link': 'https://github.com/advisories/GHSA-4rq4-32rv-6wp6', 'description': 'shelljs is vulnerable to Improper Privilege Management', 'packageVersion': '0.3.0', 'vector': 'CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H', 'packageName': 'shelljs', 'publishedDate': '2022-01-11T07:15:00Z', 'cvss': 7.1, 'status': 'fixed in 0.8.5'}, {'severity': 'critical', 'riskFactors': {'Critical severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2020-7774', 'link': 'https://github.com/advisories/GHSA-c4w7-xm78-47vh', 'description': 'The package y18n before 3.2.2, 4.0.1 and 5.0.5, is vulnerable to Prototype Pollution.', 'packageVersion': '3.2.1', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H', 'packageName': 'y18n', 'publishedDate': '2020-11-17T13:15:00Z', 'cvss': 9.8, 'status': 'fixed in 5.0.5, 4.0.1, 3.2.2'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2017-16138', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2017-16138', 'description': 'The mime module < 1.4.1, 2.0.1, 2.0.2 is vulnerable to regular expression denial of service when a mime lookup is performed on untrusted user input.', 'packageVersion': '1.2.11', 'vector': 'CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'mime', 'publishedDate': '2018-06-07T02:29:00Z', 'cvss': 7.5, 'status': 'fixed in 2.0.3, 1.4.1'}, {'severity': 'medium', 'riskFactors': {'Has fix': {}, 'Medium severity': {}, 'DoS': {}}, 'cveId': 'PRISMA-2022-0097', 'link': 'https://github.com/tapjs/tap-mocha-reporter/commit/50c8c31ed7f6ebf18de4339ee0e64b1558b07e83', 'description': 'tap-mocha-reporter package versions before 5.0.2 are vulnerable to Regular Expression Denial of Service (ReDoS) due to vulnerable return value.', 'packageVersion': '2.0.1', 'vector': '', 'packageName': 'tap-mocha-reporter', 'publishedDate': '2022-03-15T11:44:14Z', 'cvss': 5.3, 'status': 'fixed in 5.0.2'}, {'severity': 'high', 'riskFactors': {'Has fix': {}, 'High severity': {}, 'DoS': {}}, 'cveId': 'PRISMA-2022-0098', 'link': 'https://github.com/tapjs/tap-mocha-reporter/commit/57529706c268b81652297c82f55ed5e7dfc8a3b2', 'description': 'tap-mocha-reporter package versions before 5.0.2 are vulnerable to Prototype Pollution.  This package allows for modification of prototype behavior, which may result in Information Disclosure/DoS/RCE', 'packageVersion': '2.0.1', 'vector': '', 'packageName': 'tap-mocha-reporter', 'publishedDate': '2022-03-15T11:45:02Z', 'cvss': 8, 'status': 'fixed in 5.0.2'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2022-29167', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2022-29167', 'description': "Hawk is an HTTP authentication scheme providing mechanisms for making authenticated HTTP requests with partial cryptographic verification of the request and response, covering the HTTP method, request URI, host, and optionally the request payload. Hawk used a regular expression to parse `Host` HTTP header (`Hawk.utils.parseHost()`), which was subject to regular expression DoS attack - meaning each added character in the attacker\\'s input increases the computation time exponentially. `parseHost()` was patched in `9.0.1` to use built-in `URL` class to parse hostname instead. `Hawk.authenticate()` accepts `options` argument. If that contains `host` and `port`, those would be used instead of a call to `utils.parseHost()`.", 'packageVersion': '1.0.0', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'hawk', 'publishedDate': '2022-05-05T23:15:00Z', 'cvss': 7.5, 'status': 'fixed in 9.0.1'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2016-2515', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2016-2515', 'description': 'Hawk before 3.1.3 and 4.x before 4.1.1 allow remote attackers to cause a denial of service (CPU consumption or partial outage) via a long (1) header or (2) URI that is matched against an improper regular expression.', 'packageVersion': '1.0.0', 'vector': 'CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'hawk', 'publishedDate': '2016-01-19T00:00:00Z', 'cvss': 7, 'status': 'fixed in 4.1.1, 3.1.3'}, {'severity': 'critical', 'riskFactors': {'Critical severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2019-10744', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2019-10744', 'description': 'Versions of lodash lower than 4.17.12 are vulnerable to Prototype Pollution. The function defaultsDeep could be tricked into adding or modifying properties of Object.prototype using a constructor payload.', 'packageVersion': '2.4.2', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H', 'packageName': 'lodash', 'publishedDate': '2019-07-26T00:15:00Z', 'cvss': 9.1, 'status': 'fixed in 4.17.12'}, {'severity': 'high', 'riskFactors': {'Attack vector: network': {}, 'Has fix': {}, 'High severity': {}}, 'cveId': 'CVE-2020-8203', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2020-8203', 'description': 'Prototype pollution attack when using _.zipObjectDeep in lodash before 4.17.20.', 'packageVersion': '2.4.2', 'vector': 'CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H', 'packageName': 'lodash', 'publishedDate': '2020-07-15T17:15:00Z', 'cvss': 7.4, 'status': 'fixed in 4.17.20'}, {'severity': 'medium', 'riskFactors': {'Attack vector: network': {}, 'Has fix': {}, 'Medium severity': {}}, 'cveId': 'CVE-2018-16487', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2018-16487', 'description': 'A prototype pollution vulnerability was found in lodash <4.17.11 where the functions merge, mergeWith, and defaultsDeep can be tricked into adding or modifying properties of Object.prototype.', 'packageVersion': '2.4.2', 'vector': 'CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L', 'packageName': 'lodash', 'publishedDate': '2019-02-01T18:29:00Z', 'cvss': 5.6, 'status': 'fixed in 4.17.11'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2021-23337', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2021-23337', 'description': 'Lodash versions prior to 4.17.21 are vulnerable to Command Injection via the template function.', 'packageVersion': '2.4.2', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H', 'packageName': 'lodash', 'publishedDate': '2021-02-15T13:15:00Z', 'cvss': 7.2, 'status': 'fixed in 4.17.21'}, {'severity': 'medium', 'riskFactors': {'Medium severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2019-1010266', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2019-1010266', 'description': 'lodash prior to 4.17.11 is affected by: CWE-400: Uncontrolled Resource Consumption. The impact is: Denial of service. The component is: Date handler. The attack vector is: Attacker provides very long strings, which the library attempts to match using a regular expression. The fixed version is: 4.17.11.', 'packageVersion': '2.4.2', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'lodash', 'publishedDate': '2019-07-17T21:15:00Z', 'cvss': 6.5, 'status': 'fixed in 4.17.11'}, {'severity': 'medium', 'riskFactors': {'Medium severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2020-28500', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2020-28500', 'description': 'Lodash versions prior to 4.17.21 are vulnerable to Regular Expression Denial of Service (ReDoS) via the toNumber, trim and trimEnd functions.', 'packageVersion': '2.4.2', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L', 'packageName': 'lodash', 'publishedDate': '2021-02-15T11:15:00Z', 'cvss': 5.3, 'status': 'fixed in 4.17.21'}, {'severity': 'medium', 'riskFactors': {'Medium severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2018-3721', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2018-3721', 'description': 'lodash node module before 4.17.5 suffers from a Modification of Assumed-Immutable Data (MAID) vulnerability via defaultsDeep, merge, and mergeWith functions, which allows a malicious user to modify the prototype of \\"Object\\" via __proto__, causing the addition or modification of an existing property that will exist on all objects.', 'packageVersion': '2.4.2', 'vector': 'CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N', 'packageName': 'lodash', 'publishedDate': '2018-06-07T02:29:00Z', 'cvss': 6.5, 'status': 'fixed in 4.17.5'}, {'severity': 'moderate', 'riskFactors': {'Attack vector: network': {}, 'Has fix': {}, 'Medium severity': {}}, 'cveId': 'CVE-2017-16026', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2017-16026', 'description': 'Request is an http client. If a request is made using ```multipart```, and the body type is a ```number```, then the specified number of non-zero memory is passed in the body. This affects Request >=2.2.6 <2.47.0 || >2.51.0 <=2.67.0.', 'packageVersion': '2.36.0', 'vector': 'CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N', 'packageName': 'request', 'publishedDate': '2018-06-04T19:29:00Z', 'cvss': 4, 'status': 'fixed in 2.68.0, 2.68.0'}, {'severity': 'critical', 'riskFactors': {'Critical severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2018-1000620', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2018-1000620', 'description': 'Eran Hammer cryptiles version 4.1.1 earlier contains a CWE-331: Insufficient Entropy vulnerability in randomDigits() method that can result in An attacker is more likely to be able to brute force something that was supposed to be random.. This attack appear to be exploitable via Depends upon the calling application.. This vulnerability appears to have been fixed in 4.1.2.', 'packageVersion': '0.2.2', 'vector': 'CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H', 'packageName': 'cryptiles', 'publishedDate': '2018-07-19T00:00:00Z', 'cvss': 9, 'status': 'fixed in 4.1.2'}, {'severity': 'medium', 'riskFactors': {'Has fix': {}, 'Medium severity': {}}, 'cveId': 'PRISMA-2022-0087', 'link': 'https://github.com/ljharb/qs/issues/200', 'description': "qs package versions before 6.3.1 are vulnerable to Prototype Pollution. It\\'s a bypass for CVE-2017-1000048, that only fixed ]=toString, but not fixed  [=toString. So it is possible to override prototype properties such as toString() for a nested object which exceeds the depth limit even when allowPrototypes is set to false.", 'packageVersion': '0.6.6', 'vector': '', 'packageName': 'qs', 'publishedDate': '2022-03-17T09:41:42Z', 'cvss': 5.9, 'status': 'fixed in 6.3.1'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2022-24999', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2022-24999', 'description': 'qs before 6.10.3, as used in Express before 4.17.3 and other products, allows attackers to cause a Node process hang for an Express application because an __ proto__ key can be used. In many typical Express use cases, an unauthenticated remote attacker can place the attack payload in the query string of the URL that is used to visit the application, such as a[__proto__]=b&a[__proto__]&a[length]=100000000. The fix was backported to qs 6.9.7, 6.8.3, 6.7.3, 6.6.1, 6.5.3, 6.4.1, 6.3.3, and 6.2.4 (and therefore Express 4.17.3, which has \\"deps: qs@6.9.7\\" in its release description, is not vulnerable).', 'packageVersion': '0.6.6', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'qs', 'publishedDate': '2022-11-26T22:15:00Z', 'cvss': 7.5, 'status': 'fixed in 6.10.3'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2017-1000048', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2017-1000048', 'description': "the web framework using ljharb\\'s qs module older than v6.3.2, v6.2.3, v6.1.2, and v6.0.4 is vulnerable to a DoS. A malicious user can send a evil request to cause the web framework crash.", 'packageVersion': '0.6.6', 'vector': 'CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'qs', 'publishedDate': '2017-03-01T00:00:00Z', 'cvss': 7, 'status': 'fixed in 6.3.2, 6.2.3, 6.1.2, 6.0.4'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2014-7191', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2014-7191', 'description': 'The qs module before 1.0.0 in Node.js does not call the compact function for array data, which allows remote attackers to cause a denial of service (memory consumption) by using a large index value to create a sparse array.', 'packageVersion': '0.6.6', 'vector': 'AV:N/AC:L/Au:N/C:N/I:N/A:P', 'packageName': 'qs', 'publishedDate': '2014-10-19T01:55:00Z', 'cvss': 7, 'status': 'fixed in 1.0.0'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2014-10064', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2014-10064', 'description': 'The qs module before 1.0.0 does not have an option or default for specifying object depth and when parsing a string representing a deeply nested object will block the event loop for long periods of time. An attacker could leverage this to cause a temporary denial-of-service condition, for example, in a web application, other requests would not be processed while this blocking is occurring.', 'packageVersion': '0.6.6', 'vector': 'CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'qs', 'publishedDate': '2018-05-31T20:29:00Z', 'cvss': 7, 'status': 'fixed in 1.0.0'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2018-3728', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2018-3728', 'description': 'hoek node module before 4.2.0 and 5.0.x before 5.0.3 suffers from a Modification of Assumed-Immutable Data (MAID) vulnerability via \\\'merge\\\' and \\\'applyToDefaults\\\' functions, which allows a malicious user to modify the prototype of \\"Object\\" via __proto__, causing the addition or modification of an existing property that will exist on all objects.', 'packageVersion': '0.9.1', 'vector': 'CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H', 'packageName': 'hoek', 'publishedDate': '2018-03-30T19:29:00Z', 'cvss': 8.8, 'status': 'fixed in 5.0.3, 4.2.0'}, {'severity': 'high', 'riskFactors': {'Attack vector: network': {}, 'Has fix': {}, 'High severity': {}}, 'cveId': 'CVE-2020-36604', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2020-36604', 'description': 'hoek before 8.5.1 and 9.x before 9.0.3 allows prototype poisoning in the clone function.', 'packageVersion': '0.9.1', 'vector': 'CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H', 'packageName': 'hoek', 'publishedDate': '2022-09-23T06:15:00Z', 'cvss': 8.1, 'status': 'fixed in 9.0.3, 8.5.1'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}, 'Recent vulnerability': {}}, 'cveId': 'CVE-2021-33623', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2021-33623', 'description': 'The trim-newlines package before 3.0.1 and 4.x before 4.0.1 for Node.js has an issue related to regular expression denial-of-service (ReDoS) for the .end() method.', 'packageVersion': '1.0.0', 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'trim-newlines', 'publishedDate': '2021-05-28T18:15:00Z', 'cvss': 7.5, 'status': 'fixed in 4.0.1, 3.0.1'}, {'severity': 'medium', 'riskFactors': {'Has fix': {}, 'Medium severity': {}, 'DoS': {}}, 'cveId': 'PRISMA-2021-0169', 'link': 'https://github.com/mishoo/UglifyJS/pull/5134', 'description': 'uglify-js package versions before 3.14.3 are vulnerable to Regular Expression Denial of Service (ReDoS) via minify() function that uses vulnerable regex.', 'packageVersion': '2.4.24', 'vector': '', 'packageName': 'uglify-js', 'publishedDate': '2021-12-23T10:05:50Z', 'cvss': 5.3, 'status': 'fixed in 3.14.3'}, {'severity': 'high', 'riskFactors': {'High severity': {}, 'DoS': {}, 'Attack vector: network': {}, 'Has fix': {}, 'Attack complexity: low': {}}, 'cveId': 'CVE-2015-8858', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2015-8858', 'description': 'The uglify-js package before 2.6.0 for Node.js allows attackers to cause a denial of service (CPU consumption) via crafted input in a parse call, aka a \\"regular expression denial of service (ReDoS).\\"', 'packageVersion': '2.4.24', 'vector': 'CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H', 'packageName': 'uglify-js', 'publishedDate': '2017-01-23T21:59:00Z', 'cvss': 7, 'status': 'fixed in 2.6.0'}, {'severity': 'medium', 'cveId': 'CVE-2017-16137', 'link': '', 'description': '', 'packageVersion': '2.3.0', 'vector': '', 'packageName': 'helmet', 'publishedDate': '', 'cvss': 5.3, 'status': 'fixed in 3.8.2', 'fixVersion': '3.8.2', 'causePackageName': 'debug', 'causePackageVersion': '2.2.0'}, {'severity': 'moderate', 'cveId': 'CVE-2019-2391', 'link': '', 'description': '', 'packageVersion': '2.2.36', 'vector': '', 'packageName': 'mongodb', 'publishedDate': '', 'cvss': 4, 'status': 'fixed in 3.1.13', 'fixVersion': '3.1.13', 'causePackageName': 'bson', 'causePackageVersion': '1.0.9'}, {'severity': 'critical', 'cveId': 'CVE-2020-7610', 'link': '', 'description': '', 'packageVersion': '2.2.36', 'vector': '', 'packageName': 'mongodb', 'publishedDate': '', 'cvss': 9.8, 'status': 'fixed in 3.1.13', 'fixVersion': '3.1.13', 'causePackageName': 'bson', 'causePackageVersion': '1.0.9'}, {'severity': 'moderate', 'cveId': 'GHSA-c3m8-x3cg-qm2c', 'link': '', 'description': '', 'packageVersion': '2.3.0', 'vector': '', 'packageName': 'helmet', 'publishedDate': '', 'cvss': 4, 'status': 'fixed in 3.21.3', 'fixVersion': '3.21.3', 'causePackageName': 'helmet-csp', 'causePackageVersion': '1.2.2'}], 'dependencyTreeS3ObjectKey': 'dependency_tree/ajbara/ajbara_cli_repo/ScaGoat-main/1670509263116/src/dependency-tree-package-lock.json', 'email': '', 'customerName': 'ajbara', 'dependencies': {'8': [9, 10], '9': [595], '22': [23, 24], '23': [29, 36, 92, 268, 354, 357, 358, 61, 592, 593, 333, 96, 99], '24': [25], '50': [51, 52, 53, 54, 55, 56, 57], '51': [127, 53, 128, 129, 55, 130, 131, 132, 133], '52': [31, 159, 55, 160], '54': [58], '56': [379, 355], '58': [59, 60, 61], '59': [61], '60': [61], '65': [66], '76': [77, 78, 79, 80, 81, 82, 83, 84, 85, 86], '79': [248], '81': [80, 151, 346, 236, 492], '82': [495], '83': [290], '85': [77, 81, 82, 195], '86': [589, 9], '90': [49, 91], '92': [30, 36, 93, 94, 55, 95, 96, 97, 98, 99], '93': [100], '94': [93, 369, 370, 371], '96': [50, 79, 159, 93, 400, 994, 995, 996], '97': [54, 55, 997], '98': [354], '99': [268, 354, 333, 957], '101': [102, 103, 104, 105, 106], '102': [106, 110, 111], '104': [108, 109, 112], '105': [107, 115, 116, 117, 118, 119], '106': [107, 110, 120, 111, 121, 122], '109': [113, 114], '115': [135, 252, 137, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264], '117': [591], '119': [414], '127': [177, 178], '129': [128, 468, 55], '130': [93, 100, 356, 98], '131': [506], '132': [31, 128, 100, 130], '133': [1049, 55], '135': [136, 137], '137': [136, 300, 301], '138': [139], '139': [1022, 269, 151, 553, 969, 970], '148': [22, 43, 92, 149, 150, 151, 152, 153, 154, 155, 156, 157], '149': [65, 404], '150': [417, 418], '152': [64], '153': [419], '156': [427, 23, 952], '159': [161], '160': [159, 912], '161': [505, 512, 513], '168': [169, 111, 170], '170': [107, 110, 120, 111, 538, 121, 122], '171': [172, 173, 174], '172': [176, 515, 173], '173': [20], '174': [172, 173], '177': [178], '178': [55], '188': [189, 190, 191, 192], '189': [193], '190': [189, 194, 83, 195], '197': [72], '198': [199], '200': [201], '228': [229, 230, 231], '231': [948], '232': [203, 204, 228, 233], '233': [151, 234, 235, 80, 236], '252': [135, 137, 301, 253, 312, 313, 306, 256], '253': [135, 467], '254': [467], '255': [135, 467], '257': [135, 267], '259': [135, 267, 301, 258], '260': [135, 267], '261': [135, 137, 308], '262': [508, 509, 521, 306, 314], '263': [312, 313, 534, 535], '264': [46, 135, 297, 381, 467, 530], '267': [258], '268': [58, 55], '297': [135, 298, 136, 137, 299, 300, 301, 302, 303, 304, 255, 305, 306, 307, 308, 258, 259, 309, 310, 311], '298': [303, 254, 314], '299': [135, 137], '300': [136], '302': [137, 300, 261], '306': [467], '307': [135], '309': [135, 267], '310': [135, 267], '311': [136, 465, 301, 262], '314': [301], '319': [320], '320': [114], '331': [79, 159, 93, 332, 333, 96, 99], '333': [354, 957], '335': [8, 34, 76, 198, 78, 336, 204, 79, 80, 292, 194, 318, 337, 338, 339, 340, 83, 191, 341, 342, 84, 343, 199, 344, 345, 346, 236, 86, 347, 348], '337': [79, 292, 194, 83, 191, 236, 195], '342': [399, 503], '344': [79, 80, 271, 292, 194, 318, 338, 81, 594, 5, 83, 343, 236], '345': [292, 194, 191, 344], '349': [350, 204, 79, 351, 352, 191, 199, 231], '354': [41, 355], '355': [356], '356': [55], '357': [36, 54, 331, 93, 358, 333, 96, 99], '358': [400], '369': [506], '371': [369, 370], '377': [101, 275, 109, 378], '378': [121, 711, 939, 105, 170], '384': [385, 168, 175, 110, 377, 386, 117, 387, 388, 389, 390, 391, 392, 393, 394, 170], '386': [101, 148, 396, 397, 394], '387': [385, 112, 612, 613], '388': [103, 557], '390': [113, 114], '392': [937, 591], '393': [138, 990], '394': [1058, 1059, 116, 117, 1060, 119], '396': [90], '397': [319], '414': [403, 415, 151, 396, 416, 155], '415': [416, 500], '416': [500], '417': [419], '467': [301], '468': [369, 469], '469': [470], '472': [188, 276, 473, 401, 474, 475, 476, 477, 478, 479, 480, 481], '474': [142, 200, 482, 483], '477': [488], '479': [617], '505': [506], '506': [470], '508': [465], '509': [135, 467], '512': [506], '515': [516], '521': [467], '530': [46, 135, 297, 381, 467], '535': [135, 137], '559': [502], '592': [29, 36, 268, 354, 358, 536, 61, 593, 333, 96, 99], '593': [55], '604': [315, 605, 606], '605': [123, 610], '606': [68, 69, 607, 126, 206, 151, 609], '607': [608], '610': [886, 964], '613': [140, 171, 250, 865, 172, 1070, 1078], '614': [79, 82, 615], '711': [611], '839': [68], '865': [559], '912': [205, 159, 506], '952': [206, 151, 68, 938, 608, 953, 609], '953': [608], '957': [971], '969': [970], '980': [318, 338, 981, 191, 982], '995': [45, 251, 967, 998, 999], '997': [506], '1016': [390, 1017], '1017': [107, 1039, 899, 1040], '1039': [13], '1040': [798, 902, 801, 250], '1049': [1050, 839, 128]}, 'repositoryId': ''},
        '/requirements.txt': {'sourceId': 'ajbara_cli_repo/ScaGoat-main', 'type': 'Package', 'branch': '',
                              'sourceType': 'CLI', 'vulnerabilities': [
                {'cveId': 'CVE-2022-1941', 'status': 'fixed in 4.21.6, 3.20.2, 3.19.5, 3.18.3', 'severity': 'high',
                 'packageName': 'protobuf', 'packageVersion': '3.18.1',
                 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2022-1941', 'cvss': 7,
                 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H',
                 'description': 'A parsing vulnerability for the MessageSet type in the ProtocolBuffers versions prior to and including 3.16.1, 3.17.3, 3.18.2, 3.19.4, 3.20.1 and 3.21.5 for protobuf-cpp, and versions prior to and including 3.16.1, 3.17.3, 3.18.2, 3.19.4, 3.20.1 and 4.21.5 for protobuf-python can lead to out of memory failures. A specially crafted message with multiple key-value per elements creates parsing issues, and can lead to a Denial of Service against services receiving unsanitized input. We recommend upgrading to versions 3.18.3, 3.19.5, 3.20.2, 3.21.6 for protobuf-cpp and 3.18.3, 3.19.5, 3.20.2, 4.21.6 for protobuf-python. Versions for 3.16 and 3.17 are no longer updated.',
                 'riskFactors': ['Attack complexity: low', 'Attack vector: network', 'DoS', 'Has fix',
                                 'High severity',
                                 'Recent vulnerability'], 'publishedDate': '2022-09-22T15:15:00Z'},
                {'cveId': 'CVE-2021-44420', 'status': 'fixed in 3.2.10, 3.1.14, 2.2.25', 'severity': 'high',
                 'packageName': 'django', 'packageVersion': '3.2.8',
                 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2021-44420', 'cvss': 7.3,
                 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L',
                 'description': 'In Django 2.2 before 2.2.25, 3.1 before 3.1.14, and 3.2 before 3.2.10, HTTP requests for URLs with trailing newlines could bypass upstream access control based on URL paths.',
                 'riskFactors': ['Attack complexity: low', 'Attack vector: network', 'Has fix', 'High severity',
                                 'Recent vulnerability'], 'publishedDate': '2021-12-08T00:15:00Z'},
                {'cveId': 'CVE-2021-45452', 'status': 'fixed in 4.0.1, 3.2.11, 2.2.26', 'severity': 'medium',
                 'packageName': 'django', 'packageVersion': '3.2.8',
                 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2021-45452', 'cvss': 5.3,
                 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N',
                 'description': 'Storage.save in Django 2.2 before 2.2.26, 3.2 before 3.2.11, and 4.0 before 4.0.1 allows directory traversal if crafted filenames are directly passed to it.',
                 'riskFactors': ['Recent vulnerability', 'Attack complexity: low', 'Attack vector: network',
                                 'Has fix',
                                 'Medium severity'], 'publishedDate': '2022-01-05T00:15:00Z'},
                {'cveId': 'CVE-2021-45116', 'status': 'fixed in 4.0.1, 3.2.11, 2.2.26', 'severity': 'high',
                 'packageName': 'django', 'packageVersion': '3.2.8',
                 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2021-45116', 'cvss': 7.5,
                 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N',
                 'description': "An issue was discovered in Django 2.2 before 2.2.26, 3.2 before 3.2.11, and 4.0 before 4.0.1. Due to leveraging the Django Template Language\\'s variable resolution logic, the dictsort template filter was potentially vulnerable to information disclosure, or an unintended method call, if passed a suitably crafted key.",
                 'riskFactors': ['Attack complexity: low', 'Attack vector: network', 'Has fix', 'High severity',
                                 'Recent vulnerability'], 'publishedDate': '2022-01-05T00:15:00Z'},
                {'cveId': 'CVE-2021-45115', 'status': 'fixed in 4.0.1, 3.2.11, 2.2.26', 'severity': 'high',
                 'packageName': 'django', 'packageVersion': '3.2.8',
                 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2021-45115', 'cvss': 7.5,
                 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H',
                 'description': 'An issue was discovered in Django 2.2 before 2.2.26, 3.2 before 3.2.11, and 4.0 before 4.0.1. UserAttributeSimilarityValidator incurred significant overhead in evaluating a submitted password that was artificially large in relation to the comparison values. In a situation where access to user registration was unrestricted, this provided a potential vector for a denial-of-service attack.',
                 'riskFactors': ['Recent vulnerability', 'Attack complexity: low', 'Attack vector: network', 'DoS',
                                 'Has fix', 'High severity'], 'publishedDate': '2022-01-05T00:15:00Z'},
                {'cveId': 'CVE-2022-22818', 'status': 'fixed in 4.0.2, 3.2.12, 2.2.27', 'severity': 'medium',
                 'packageName': 'django', 'packageVersion': '3.2.8',
                 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2022-22818', 'cvss': 6.1,
                 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N',
                 'description': 'The {% debug %} template tag in Django 2.2 before 2.2.27, 3.2 before 3.2.12, and 4.0 before 4.0.2 does not properly encode the current context. This may lead to XSS.',
                 'riskFactors': ['Recent vulnerability', 'Attack complexity: low', 'Attack vector: network',
                                 'Has fix',
                                 'Medium severity'], 'publishedDate': '2022-02-03T02:15:00Z'},
                {'cveId': 'CVE-2022-23833', 'status': 'fixed in 4.0.2, 3.2.12, 2.2.27', 'severity': 'high',
                 'packageName': 'django', 'packageVersion': '3.2.8',
                 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2022-23833', 'cvss': 7.5,
                 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H',
                 'description': 'An issue was discovered in MultiPartParser in Django 2.2 before 2.2.27, 3.2 before 3.2.12, and 4.0 before 4.0.2. Passing certain inputs to multipart forms could result in an infinite loop when parsing files.',
                 'riskFactors': ['Attack complexity: low', 'Attack vector: network', 'Has fix', 'High severity',
                                 'Recent vulnerability'], 'publishedDate': '2022-02-03T02:15:00Z'},
                {'cveId': 'CVE-2022-28346', 'status': 'fixed in 4.0.4, 3.2.13, 2.2.28', 'severity': 'critical',
                 'packageName': 'django', 'packageVersion': '3.2.8',
                 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2022-28346', 'cvss': 9.8,
                 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H',
                 'description': 'An issue was discovered in Django 2.2 before 2.2.28, 3.2 before 3.2.13, and 4.0 before 4.0.4. QuerySet.annotate(), aggregate(), and extra() methods are subject to SQL injection in column aliases via a crafted dictionary (with dictionary expansion) as the passed **kwargs.',
                 'riskFactors': ['Recent vulnerability', 'Attack complexity: low', 'Attack vector: network',
                                 'Critical severity', 'Has fix'], 'publishedDate': '2022-04-12T05:15:00Z'},
                {'cveId': 'CVE-2022-28347', 'status': 'fixed in 4.0.4, 3.2.13, 2.2.28', 'severity': 'critical',
                 'packageName': 'django', 'packageVersion': '3.2.8',
                 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2022-28347', 'cvss': 9.8,
                 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H',
                 'description': 'A SQL injection issue was discovered in QuerySet.explain() in Django 2.2 before 2.2.28, 3.2 before 3.2.13, and 4.0 before 4.0.4. This occurs by passing a crafted dictionary (with dictionary expansion) as the **options argument, and placing the injection payload in an option name.',
                 'riskFactors': ['Recent vulnerability', 'Attack complexity: low', 'Attack vector: network',
                                 'Critical severity', 'Has fix'], 'publishedDate': '2022-04-12T05:15:00Z'},
                {'cveId': 'CVE-2022-36359', 'status': 'fixed in 4.0.7, 4.0, 3.2.15', 'severity': 'high',
                 'packageName': 'django', 'packageVersion': '3.2.8',
                 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2022-36359', 'cvss': 8.8,
                 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H',
                 'description': 'An issue was discovered in the HTTP FileResponse class in Django 3.2 before 3.2.15 and 4.0 before 4.0.7. An application is vulnerable to a reflected file download (RFD) attack that sets the Content-Disposition header of a FileResponse when the filename is derived from user-supplied input.',
                 'riskFactors': ['Has fix', 'High severity', 'Recent vulnerability', 'Attack complexity: low',
                                 'Attack vector: network'], 'publishedDate': '2022-08-03T14:15:00Z'},
                {'cveId': 'CVE-2022-34265', 'status': 'fixed in 4.0.6, 4.0, 3.2.14', 'severity': 'critical',
                 'packageName': 'django', 'packageVersion': '3.2.8',
                 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2022-34265', 'cvss': 9.8,
                 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H',
                 'description': 'An issue was discovered in Django 3.2 before 3.2.14 and 4.0 before 4.0.6. The Trunc() and Extract() database functions are subject to SQL injection if untrusted data is used as a kind/lookup_name value. Applications that constrain the lookup name and kind choice to a known safe list are unaffected.',
                 'riskFactors': ['Attack complexity: low', 'Attack vector: network', 'Critical severity', 'Has fix',
                                 'Recent vulnerability'], 'publishedDate': '2022-07-04T16:15:00Z'},
                {'cveId': 'CVE-2022-41323', 'status': 'fixed in 4.1.2, 4.0.8, 3.2.16', 'severity': 'high',
                 'packageName': 'django', 'packageVersion': '3.2.8',
                 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2022-41323', 'cvss': 7.5,
                 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H',
                 'description': 'In Django 3.2 before 3.2.16, 4.0 before 4.0.8, and 4.1 before 4.1.2, internationalized URLs were subject to a potential denial of service attack via the locale parameter, which is treated as a regular expression.',
                 'riskFactors': ['Has fix', 'High severity', 'Recent vulnerability', 'Attack complexity: low',
                                 'Attack vector: network', 'DoS'], 'publishedDate': '2022-10-16T06:15:00Z'},
                {'cveId': 'CVE-2022-35918', 'status': 'fixed in 1.11.1', 'severity': 'moderate',
                 'packageName': 'streamlit', 'packageVersion': '0.88.0',
                 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2022-35918', 'cvss': 4,
                 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N',
                 'description': 'Streamlit is a data oriented application development framework for python. Users hosting Streamlit app(s) that use custom components are vulnerable to a directory traversal attack that could leak data from their web server file-system such as: server logs, world readable files, and potentially other sensitive information. An attacker can craft a malicious URL with file paths and the streamlit server would process that URL and return the contents of that file. This issue has been resolved in version 1.11.1. Users are advised to upgrade. There are no known workarounds for this issue.',
                 'riskFactors': ['Attack complexity: low', 'Attack vector: network', 'Has fix', 'Medium severity',
                                 'Recent vulnerability'], 'publishedDate': '2022-08-06T05:51:50Z'},
                {'cveId': 'CVE-2021-23727', 'status': 'fixed in 5.2.2', 'severity': 'high', 'packageName': 'celery',
                 'packageVersion': '5.1.2', 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2021-23727', 'cvss': 7.5,
                 'vector': 'CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H',
                 'description': 'This affects the package celery before 5.2.2. It by default trusts the messages and metadata stored in backends (result stores). When reading task metadata from the backend, the data is deserialized. Given that an attacker can gain access to, or somehow manipulate the metadata within a celery backend, they could trigger a stored command injection vulnerability and potentially gain further access to the system.',
                 'riskFactors': ['Attack vector: network', 'Has fix', 'High severity', 'Recent vulnerability'],
                 'publishedDate': '2021-12-29T17:15:00Z'},
                {'cveId': 'PRISMA-2021-0198', 'status': 'fixed in 3.8.0a0', 'severity': 'high',
                 'packageName': 'aiohttp',
                 'packageVersion': '3.7.4', 'link': 'https://github.com/aio-libs/aiohttp/issues/4818', 'cvss': 7.5,
                 'vector': None,
                 'description': 'aiohttp package versions before 3.8.0a0 are vulnerable to HTTP Header Injection. aiohttp concatenating server-response\\\\client-request header without any validation, some of the header values based on user input. An attacker can craft urls that will force this handler to return any custom http-headers, or skip some of the existing ones, or break http payload',
                 'riskFactors': ['Has fix', 'High severity'], 'publishedDate': '2021-12-23T15:55:14Z'},
                {'cveId': 'CVE-2022-35920', 'status': 'fixed in 22.6.1, 21.12.2, 20.12.7', 'severity': 'high',
                 'packageName': 'sanic', 'packageVersion': '21.9.1',
                 'link': 'https://nvd.nist.gov/vuln/detail/CVE-2022-35920', 'cvss': 7.5,
                 'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N',
                 'description': 'Sanic is an opensource python web server/framework. Affected versions of sanic allow access to lateral directories when using `app.static` if using encoded `%2F` URLs. Parent directory traversal is not impacted. Users are advised to upgrade. There is no known workaround for this issue.',
                 'riskFactors': ['Attack vector: network', 'Has fix', 'High severity', 'Recent vulnerability',
                                 'Attack complexity: low'], 'publishedDate': '2022-08-01T22:15:00Z'}],
                              'name': 'requirements.txt', 'filePath': '/requirements.txt', 'fileContent': None,
                              'packages': [{'type': 'python', 'name': 'wrapt', 'version': '1.13.2', 'licenses': []},
                                           {'type': 'python', 'name': 'elasticsearch', 'version': '7.15.1',
                                            'licenses': []},
                                           {'type': 'python', 'name': 'streamlit', 'version': '0.88.0',
                                            'licenses': []},
                                           {'type': 'python', 'name': 'uvicorn', 'version': '0.11.8',
                                            'licenses': []},
                                           {'type': 'python', 'name': 'multidict', 'version': '5.2.0',
                                            'licenses': []},
                                           {'type': 'python', 'name': 'pyramid', 'version': '2.0', 'licenses': []},
                                           {'type': 'python', 'name': 'mysqlclient', 'version': '2.1.0',
                                            'licenses': []},
                                           {'type': 'python', 'name': 'uvicorn', 'version': '0.16.0',
                                            'licenses': []},
                                           {'type': 'python', 'name': 'fastapi', 'version': '0.70.1',
                                            'licenses': []},
                                           {'type': 'python', 'name': 'requests', 'version': '2.26.0',
                                            'licenses': []},
                                           {'type': 'python', 'name': 'urllib3', 'version': '1.26.7',
                                            'licenses': []},
                                           {'type': 'python', 'name': 'django', 'version': '3.2.8', 'licenses': []},
                                           {'type': 'python', 'name': 'psycopg', 'version': '3.0.1',
                                            'licenses': []},
                                           {'type': 'python', 'name': 'kafka-python', 'version': '2.0',
                                            'licenses': []},
                                           {'type': 'python', 'name': 'hug', 'version': '2.6.1', 'licenses': []},
                                           {'type': 'python', 'name': 'redis', 'version': '3.5.3', 'licenses': []},
                                           {'type': 'python', 'name': 'pymongo', 'version': '3.12.0',
                                            'licenses': []},
                                           {'type': 'python', 'name': 'tornado', 'version': '6.1', 'licenses': []},
                                           {'type': 'python', 'name': 'grpcio_tools', 'version': '1.41.0',
                                            'licenses': []},
                                           {'type': 'python', 'name': 'testcontainers', 'version': '3.4.2',
                                            'licenses': []},
                                           {'type': 'python', 'name': 'flask', 'version': '2.0.2', 'licenses': []},
                                           {'type': 'python', 'name': 'gevent', 'version': '21.8.0',
                                            'licenses': []},
                                           {'type': 'python', 'name': 'packaging', 'version': '21.0',
                                            'licenses': []},
                                           {'type': 'python', 'name': 'contextvars', 'version': '2.4',
                                            'licenses': []},
                                           {'type': 'python', 'name': 'yarl', 'version': '1.7.0', 'licenses': []},
                                           {'type': 'python', 'name': 'gunicorn', 'version': '20.1.0',
                                            'licenses': []},
                                           {'type': 'python', 'name': 'pyyaml', 'version': '6.0', 'licenses': []},
                                           {'type': 'python', 'name': 'pytest', 'version': '', 'licenses': []},
                                           {'type': 'python', 'name': 'celery', 'version': '5.1.2', 'licenses': []},
                                           {'type': 'python', 'name': 'pika', 'version': '1.2.0', 'licenses': []},
                                           {'type': 'python', 'name': 'pymysql', 'version': '1.0.2',
                                            'licenses': []},
                                           {'type': 'python', 'name': 'aiohttp', 'version': '3.7.4',
                                            'licenses': []},
                                           {'type': 'python', 'name': 'protobuf', 'version': '3.18.1',
                                            'licenses': []},
                                           {'type': 'python', 'name': 'sanic', 'version': '21.9.1', 'licenses': []},
                                           {'type': 'python', 'name': 'werkzeug', 'version': '2.0.2',
                                            'licenses': []}],
                              'cicdDetails': {'runId': 1, 'pr': '', 'commit': '', 'scaCliScanId': '1670509263116'},
                              'customerName': 'ajbara', 'email': 'ajbara@paloaltonetworks.com',
                              'license_statuses': [
                                  {'packageName': 'pymysql', 'packageVersion': '1.0.2', 'packageLang': 'python',
                                   'license': 'MIT',
                                   'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'pyyaml', 'packageVersion': '6.0', 'packageLang': 'python',
                                   'license': 'MIT',
                                   'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'pika', 'packageVersion': '1.2.0', 'packageLang': 'python',
                                   'license': 'OSI_BSD',
                                   'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'requests', 'packageVersion': '2.26.0', 'packageLang': 'python',
                                   'license': 'OSI_APACHE',
                                   'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'kafka-python', 'packageVersion': '2.0', 'packageLang': 'python',
                                   'license': 'OSI_APACHE',
                                   'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'pyramid', 'packageVersion': '2.0', 'packageLang': 'python',
                                   'license': 'BSD-derived (Repoze)', 'status': 'OPEN', 'policy': 'BC_LIC_2'},
                                  {'packageName': 'multidict', 'packageVersion': '5.2.0', 'packageLang': 'python',
                                   'license': 'OSI_APACHE',
                                   'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'tornado', 'packageVersion': '6.1', 'packageLang': 'python',
                                   'license': 'OSI_APACHE',
                                   'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'protobuf', 'packageVersion': '3.18.1', 'packageLang': 'python',
                                   'license': '3-Clause BSD License', 'status': 'OPEN', 'policy': 'BC_LIC_2'},
                                  {'packageName': 'django', 'packageVersion': '3.2.8', 'packageLang': 'python',
                                   'license': 'OSI_BSD',
                                   'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'gunicorn', 'packageVersion': '20.1.0', 'packageLang': 'python',
                                   'license': 'MIT',
                                   'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'wrapt', 'packageVersion': '1.13.2', 'packageLang': 'python',
                                   'license': 'OSI_BSD',
                                   'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'packaging', 'packageVersion': '21.0', 'packageLang': 'python',
                                   'license': 'OSI_APACHE',
                                   'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'packaging', 'packageVersion': '21.0', 'packageLang': 'python',
                                   'license': 'OSI_BSD',
                                   'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'urllib3', 'packageVersion': '1.26.7', 'packageLang': 'python',
                                   'license': 'MIT',
                                   'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'aiohttp', 'packageVersion': '3.7.4', 'packageLang': 'python',
                                   'license': 'OSI_APACHE',
                                   'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'grpcio_tools', 'packageVersion': '1.41.0',
                                   'packageLang': 'python',
                                   'license': 'OSI_APACHE', 'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'contextvars', 'packageVersion': '2.4', 'packageLang': 'python',
                                   'license': 'OSI_APACHE',
                                   'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'redis', 'packageVersion': '3.5.3', 'packageLang': 'python',
                                   'license': 'MIT',
                                   'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'sanic', 'packageVersion': '21.9.1', 'packageLang': 'python',
                                   'license': 'MIT',
                                   'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'hug', 'packageVersion': '2.6.1', 'packageLang': 'python',
                                   'license': 'MIT',
                                   'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'celery', 'packageVersion': '5.1.2', 'packageLang': 'python',
                                   'license': 'OSI_BSD',
                                   'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'mysqlclient', 'packageVersion': '2.1.0', 'packageLang': 'python',
                                   'license': 'GPL-1.0',
                                   'status': 'OPEN', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'werkzeug', 'packageVersion': '2.0.2', 'packageLang': 'python',
                                   'license': 'OSI_BSD',
                                   'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'testcontainers', 'packageVersion': '3.4.2',
                                   'packageLang': 'python',
                                   'license': 'OSI_APACHE', 'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'flask', 'packageVersion': '2.0.2', 'packageLang': 'python',
                                   'license': 'OSI_BSD',
                                   'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'gevent', 'packageVersion': '21.8.0', 'packageLang': 'python',
                                   'license': 'MIT',
                                   'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'yarl', 'packageVersion': '1.7.0', 'packageLang': 'python',
                                   'license': 'OSI_APACHE',
                                   'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'fastapi', 'packageVersion': '0.70.1', 'packageLang': 'python',
                                   'license': 'MIT',
                                   'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'psycopg', 'packageVersion': '3.0.1', 'packageLang': 'python',
                                   'license': 'LGPL-3.0',
                                   'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'pymongo', 'packageVersion': '3.12.0', 'packageLang': 'python',
                                   'license': 'OSI_APACHE',
                                   'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'elasticsearch', 'packageVersion': '7.15.1',
                                   'packageLang': 'python',
                                   'license': 'OSI_APACHE', 'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'uvicorn', 'packageVersion': '0.16.0', 'packageLang': 'python',
                                   'license': 'OSI_BSD',
                                   'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'streamlit', 'packageVersion': '0.88.0', 'packageLang': 'python',
                                   'license': 'Apache-2.0',
                                   'status': 'COMPLIANT', 'policy': 'BC_LIC_1'},
                                  {'packageName': 'uvicorn', 'packageVersion': '0.11.8', 'packageLang': 'python',
                                   'license': 'OSI_BSD',
                                   'status': 'COMPLIANT', 'policy': 'BC_LIC_1'}]}
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
    # package_mocker.patch()
    def none() -> None:
        pass

    bc_integration.set_s3_integration = none

    os.chdir(str(Path(__file__).parent.parent.parent))
    return Runner().run(root_folder=EXAMPLES_DIR)


@pytest.fixture(scope='package')
@mock.patch.dict(os.environ, {'CHECKOV_RUN_SCA_PACKAGE_SCAN_V2': 'true'})
def sca_package_report_dt(package_mocker: MockerFixture, scan_results_dt: Dict[str, Any]) -> Generator[Report, None, None]:
    orig_bc_api_key = bc_integration.bc_api_key
    orig_bc_source = bc_integration.bc_source
    orig_timestamp = bc_integration.timestamp
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    bc_integration.timestamp = "1700692537"
    bc_integration.bc_source = None

    scanner_mock = MagicMock()
    scanner_mock.return_value.scan.return_value = scan_results_dt
    package_mocker.patch("checkov.sca_package_2.runner.Scanner", side_effect=scanner_mock)
    os.chdir(str(Path(__file__).parent.parent.parent))

    yield Runner().run(root_folder=EXAMPLES_DIR)

    bc_integration.bc_api_key = orig_bc_api_key
    bc_integration.bc_source = orig_bc_source
    bc_integration.timestamp = orig_timestamp


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
                     'description': '', 'riskFactorsV2': {}, 'publishedDate': '',
                     'status': 'fixed in 7.2.0', 'lowest_fixed_version': '7.2.0'},
         'root_package_version': '3.8.3', 'root_package_name': 'cypress'},
        {'details': {'cveId': 'CVE-2021-44906', 'severity': 'critical', 'packageName': 'minimist',
                     'packageVersion': '1.2.5',
                     'link': '', 'cvss': 9.8,
                     'vector': '',
                     'description': '',
                     'riskFactorsV2': {},
                     'publishedDate': '', 'status': 'fixed in 1.2.6'}, 'root_package_name': 'forever',
         'root_package_version': '2.0.0'},
        {'details': {'cveId': 'CVE-2022-21803', 'severity': 'high', 'packageName': 'nconf', 'packageVersion': '0.6.9',
                     'link': '', 'cvss': 7.5, 'vector': '',
                     'description': '',
                     'riskFactorsV2': {},
                     'publishedDate': '', 'status': 'fixed in 0.11.4'}, 'root_package_name': 'forever',
         'root_package_version': '2.0.0'},
        {'details': {'cveId': 'CVE-2020-7598', 'severity': 'medium', 'packageName': 'minimist',
                     'packageVersion': '0.0.10',
                     'link': '', 'cvss': 5.6,
                     'vector': '',
                     'description': '',
                     'riskFactorsV2': {},
                     'publishedDate': '', 'status': 'fixed in 1.2.2',
                     }, 'root_package_name': 'forever', 'root_package_version': '2.0.0'},
        {'details': {'cveId': 'CVE-2021-44906', 'severity': 'critical', 'packageName': 'minimist',
                     'packageVersion': '0.0.10',
                     'link': '', 'cvss': 9.8,
                     'vector': '',
                     'description': '',
                     'riskFactorsV2': {},
                     'publishedDate': '', 'status': 'fixed in 1.2.6'}, 'root_package_name': 'forever',
         'root_package_version': '2.0.0'},
        {'details': {'cveId': 'PRISMA-2022-0049', 'severity': 'high', 'packageName': 'unset-value',
                     'packageVersion': '1.0.0',
                     'link': '',
                     'cvss': 8, 'vector': '',
                     'description': '',
                     'riskFactorsV2': {}, 'status': 'fixed in 2.0.1',
                     'publishedDate': ''}, 'root_package_name': 'forever',
         'root_package_version': '2.0.0'},
        {'details': {'cveId': 'CVE-2020-28469', 'severity': 'high', 'packageName': 'glob-parent',
                     'packageVersion': '3.1.0',
                     'link': '', 'cvss': 7.5,
                     'vector': '',
                     'description': '',
                     'riskFactorsV2': {}, 'publishedDate': '', 'status': 'fixed in 5.1.2'},
         'root_package_name': 'forever', 'root_package_version': '2.0.0'},
        {'details': {'cveId': 'CVE-2022-38900', 'severity': 'low', 'packageName': 'decode-uri-component',
                     'packageVersion': '0.2.0',
                     'link': '', 'cvss': 1,
                     'vector': '',
                     'description': '',
                     'riskFactorsV2': {}, 'publishedDate': '', 'status': 'fixed in 0.2.1'},
         'root_package_name': 'forever', 'root_package_version': '2.0.0'},
        {'details': {'cveId': 'CVE-2022-21803', 'severity': 'high', 'packageName': 'nconf', 'packageVersion': '0.10.0',
                     'link': '', 'cvss': 7.5,
                     'vector': '',
                     'description': '',
                     'riskFactorsV2': {},
                     'publishedDate': '', 'status': 'fixed in 0.11.4'}, 'root_package_name': 'forever',
         'root_package_version': '2.0.0'},
        {'details': {'cveId': 'CVE-2022-1537', 'severity': 'high', 'packageName': 'grunt', 'packageVersion': '1.4.1',
                     'link': '', 'cvss': 7,
                     'vector': '',
                     'description': '',
                     'riskFactorsV2': {},
                     'publishedDate': '', 'status': 'fixed in 1.5.3'}, 'root_package_name': 'grunt',
         'root_package_version': '1.4.1'},
        {'details': {'cveId': 'CVE-2022-0436', 'severity': 'medium', 'packageName': 'grunt', 'packageVersion': '1.4.1',
                     'link': '', 'cvss': 5.5,
                     'vector': '',
                     'description': '',
                     'riskFactorsV2': {}, 'publishedDate': '', 'status': 'fixed in 1.5.2'},
         'root_package_name': 'grunt', 'root_package_version': '1.4.1'},
        {'details': {'cveId': 'CVE-2017-16137', 'severity': 'medium', 'packageName': 'debug', 'packageVersion': '2.2.0',
                     'link': '', 'cvss': 5.3,
                     'vector': '',
                     'description': '',
                     'riskFactorsV2': {}, 'publishedDate': '', 'status': 'fixed in 3.1.0, 2.6.9'},
         'root_package_name': 'helmet', 'root_package_version': '2.3.0', 'root_package_fix_version': '2.4.0'},
        {'details': {'cveId': 'GHSA-C3M8-X3CG-QM2C', 'severity': 'medium', 'packageName': 'helmet-csp',
                     'packageVersion': '1.2.2', 'link': '', 'cvss': 4, 'vector': '',
                     'description': '',
                     'riskFactorsV2': {}, 'publishedDate': '', 'status': 'fixed in 2.9.1',
                     'rootPackageFixedVersion': '2.4.0'},
         'root_package_name': 'helmet', 'root_package_version': '2.3.0'},
        {'details': {'cveId': 'GHSA-C3M8-X3CG-QM2C', 'severity': 'medium', 'packageName': 'helmet',
                     'packageVersion': '2.3.0', 'link': '', 'cvss': 4, 'vector': '',
                     'description': '', 'riskFactorsV2': {}, 'publishedDate': '', 'status': 'fixed in 2.4.0'},
         'root_package_name': 'helmet', 'root_package_version': '2.3.0'},
        {'details': {'cveId': 'PRISMA-2021-0013', 'severity': 'medium', 'packageName': 'marked',
                     'packageVersion': '0.3.9',
                     'link': '', 'cvss': 0, 'vector': '',
                     'description': '',
                     'riskFactorsV2': {},
                     'publishedDate': '', 'status': 'fixed in 1.1.1'}, 'root_package_name': 'marked',
         'root_package_version': '0.3.9'},
        {'details': {'cveId': 'CVE-2022-21681', 'severity': 'high', 'packageName': 'marked', 'packageVersion': '0.3.9',
                     'link': '', 'cvss': 7.5,
                     'vector': '',
                     'description': '',
                     'riskFactorsV2': {},
                     'publishedDate': '', 'status': 'fixed in 4.0.10'}, 'root_package_name': 'marked',
         'root_package_version': '0.3.9'},
        {'details': {'cveId': 'CVE-2022-21680', 'severity': 'high', 'packageName': 'marked', 'packageVersion': '0.3.9',
                     'link': '', 'cvss': 7.5,
                     'vector': '',
                     'description': '',
                     'riskFactorsV2': {},
                     'publishedDate': '', 'status': 'fixed in 4.0.10'}, 'root_package_name': 'marked',
         'root_package_version': '0.3.9'},
        {'details': {'cveId': 'PRISMA-2022-0230', 'severity': 'high', 'packageName': 'mocha', 'packageVersion': '2.5.3',
                     'link': '', 'cvss': 7.5, 'vector': '',
                     'description': '',
                     'riskFactorsV2': {}, 'publishedDate': '', 'status': 'open'},
         'root_package_name': 'mocha', 'root_package_version': '2.5.3'},
        {'details': {'cveId': 'PRISMA-2022-0335', 'severity': 'medium', 'packageName': 'mocha',
                     'packageVersion': '2.5.3',
                     'link': '',
                     'cvss': 5.3, 'vector': '',
                     'description': '',
                     'riskFactorsV2': {}, 'publishedDate': '', 'status': 'open'},
         'root_package_name': 'mocha', 'root_package_version': '2.5.3'},
        {'details': {'cveId': 'GHSA-MH5C-679W-HH4R', 'severity': 'high', 'packageName': 'mongodb',
                     'packageVersion': '2.2.36',
                     'link': '', 'cvss': 7, 'vector': '', 'description': '',
                     'riskFactorsV2': {},
                     'publishedDate': '', 'status': 'fixed in 3.1.13'}, 'root_package_name': 'mongodb',
         'root_package_version': '2.2.36'},
        {'details': {'cveId': 'CVE-2019-2391', 'severity': 'medium', 'packageName': 'bson', 'packageVersion': '1.0.9',
                     'link': '', 'cvss': 4, 'vector': '', 'description': '',
                     'riskFactorsV2': {}, 'publishedDate': '', 'status': 'fixed in 1.1.4'
                     }, 'root_package_name': 'mongodb', 'root_package_version': '2.2.36'},
        {'details': {'cveId': 'CVE-2020-7610', 'severity': 'critical', 'packageName': 'bson', 'packageVersion': '1.0.9',
                     'link': '', 'cvss': 9.8,
                     'vector': '',
                     'description': '',
                     'riskFactorsV2': {}, 'publishedDate': '', 'status': 'fixed in 1.1.4'
                     }, 'root_package_name': 'mongodb', 'root_package_version': '2.2.36'},
        {'details': {'cveId': 'CVE-2020-7598', 'severity': 'medium', 'packageName': 'minimist',
                     'packageVersion': '0.0.10',
                     'link': '', 'cvss': 5.6, 'vector': '', 'description': '',
                     'riskFactorsV2': {},
                     'publishedDate': '', 'status': 'fixed in 1.2.2'}, 'root_package_name': 'swig',
         'root_package_version': '1.4.2'},
        {'details': {'cveId': 'CVE-2021-44906', 'severity': 'critical', 'packageName': 'minimist',
                     'packageVersion': '0.0.10',
                     'link': '', 'cvss': 9.8,
                     'vector': '',
                     'description': '',
                     'riskFactorsV2': {},
                     'publishedDate': '', 'status': 'fixed in 1.2.6'}, 'root_package_name': 'swig',
         'root_package_version': '1.4.2'},
        {'details': {'cveId': 'PRISMA-2021-0169', 'severity': 'medium', 'packageName': 'uglify-js',
                     'packageVersion': '2.4.24', 'link': '',
                     'cvss': 5.3, 'vector': '',
                     'description': '',
                     'riskFactorsV2': {},
                     'publishedDate': '', 'status': 'fixed in 3.14.3'}, 'root_package_name': 'swig',
         'root_package_version': '1.4.2'},
        {'details': {'cveId': 'CVE-2015-8858', 'severity': 'high', 'packageName': 'uglify-js',
                     'packageVersion': '2.4.24',
                     'link': '', 'cvss': 7,
                     'vector': '',
                     'description': '',
                     'riskFactorsV2': {}, 'publishedDate': '', 'status': 'fixed in 2.6.0'},
         'root_package_name': 'swig', 'root_package_version': '1.4.2'}
    ]

def get_vulnerabilities_details_package_lock_json() -> List[Dict[str, Any]]:
    return [
        {'details': {'cveId': 'PRISMA-2021-0070', 'severity': 'medium', 'packageName': 'cypress',
                     'packageVersion': '3.8.3', 'link': '', 'cvss': 0, 'vector': '',
                     'description': '', 'riskFactorsV2': {}, 'publishedDate': '',
                     'status': 'fixed in 7.2.0', 'lowest_fixed_version': '7.2.0'},
         'root_package_version': '3.8.3', 'root_package_name': 'cypress'},
        {'details': {'cveId': 'CVE-2021-44906', 'severity': 'critical', 'packageName': 'minimist',
                     'packageVersion': '1.2.5',
                     'link': '', 'cvss': 9.8,
                     'vector': '',
                     'description': '',
                     'riskFactorsV2': {},
                     'publishedDate': '', 'status': 'fixed in 1.2.6'}, 'root_package_name': 'forever',
         'root_package_version': '2.0.0'},
        {'details': {'cveId': 'CVE-2022-21803', 'severity': 'high', 'packageName': 'nconf', 'packageVersion': '0.6.9',
                     'link': '', 'cvss': 7.5, 'vector': '',
                     'description': '',
                     'riskFactorsV2': {},
                     'publishedDate': '', 'status': 'fixed in 0.11.4'}, 'root_package_name': 'forever',
         'root_package_version': '2.0.0'},
        {'details': {'cveId': 'CVE-2002-21803', 'severity': 'high', 'packageName': 'nconf', 'packageVersion': '0.6.9',
                     'link': '', 'cvss': 7.5, 'vector': '',
                     'description': '',
                     'riskFactorsV2': {},
                     'publishedDate': '', 'status': 'fixed in 0.11.4'}, 'root_package_name': 'forever',
         'root_package_version': '2.0.0'},
        {'details': {'cveId': 'CVE-2020-7598', 'severity': 'medium', 'packageName': 'minimist',
                     'packageVersion': '0.0.10',
                     'link': '', 'cvss': 5.6,
                     'vector': '',
                     'description': '',
                     'riskFactorsV2': {},
                     'publishedDate': '', 'status': 'fixed in 1.2.2',
                     }, 'root_package_name': 'forever', 'root_package_version': '2.0.0'},
        {'details': {'cveId': 'CVE-2021-44906', 'severity': 'critical', 'packageName': 'minimist',
                     'packageVersion': '0.0.10',
                     'link': '', 'cvss': 9.8,
                     'vector': '',
                     'description': '',
                     'riskFactorsV2': {},
                     'publishedDate': '', 'status': 'fixed in 1.2.6'}, 'root_package_name': 'forever',
         'root_package_version': '2.0.0'},
        {'details': {'cveId': 'PRISMA-2022-0049', 'severity': 'high', 'packageName': 'unset-value',
                     'packageVersion': '1.0.0',
                     'link': '',
                     'cvss': 8, 'vector': '',
                     'description': '',
                     'riskFactorsV2': {}, 'status': 'fixed in 2.0.1',
                     'publishedDate': ''}, 'root_package_name': 'forever',
         'root_package_version': '2.0.0'},
        {'details': {'cveId': 'CVE-2020-28469', 'severity': 'high', 'packageName': 'glob-parent',
                     'packageVersion': '3.1.0',
                     'link': '', 'cvss': 7.5,
                     'vector': '',
                     'description': '',
                     'riskFactorsV2': {}, 'publishedDate': '', 'status': 'fixed in 5.1.2'},
         'root_package_name': 'forever', 'root_package_version': '2.0.0'},
        {'details': {'cveId': 'CVE-2022-38900', 'severity': 'low', 'packageName': 'decode-uri-component',
                     'packageVersion': '0.2.0',
                     'link': '', 'cvss': 1,
                     'vector': '',
                     'description': '',
                     'riskFactorsV2': {}, 'publishedDate': '', 'status': 'fixed in 0.2.1'},
         'root_package_name': 'forever', 'root_package_version': '2.0.0'},
        {'details': {'cveId': 'CVE-2022-21803', 'severity': 'high', 'packageName': 'nconf', 'packageVersion': '0.10.0',
                     'link': '', 'cvss': 7.5,
                     'vector': '',
                     'description': '',
                     'riskFactorsV2': {},
                     'publishedDate': '', 'status': 'fixed in 0.11.4'}, 'root_package_name': 'forever',
         'root_package_version': '2.0.0'},
        {'details': {'cveId': 'CVE-2022-1537', 'severity': 'high', 'packageName': 'grunt', 'packageVersion': '1.4.1',
                     'link': '', 'cvss': 7,
                     'vector': '',
                     'description': '',
                     'riskFactorsV2': {},
                     'publishedDate': '', 'status': 'fixed in 1.5.3'}, 'root_package_name': 'grunt',
         'root_package_version': '1.4.1'},
        {'details': {'cveId': 'CVE-2022-0436', 'severity': 'medium', 'packageName': 'grunt', 'packageVersion': '1.4.1',
                     'link': '', 'cvss': 5.5,
                     'vector': '',
                     'description': '',
                     'riskFactorsV2': {}, 'publishedDate': '', 'status': 'fixed in 1.5.2'},
         'root_package_name': 'grunt', 'root_package_version': '1.4.1'},
        {'details': {'cveId': 'CVE-2017-16137', 'severity': 'medium', 'packageName': 'debug', 'packageVersion': '2.2.0',
                     'link': '', 'cvss': 5.3,
                     'vector': '',
                     'description': '',
                     'riskFactorsV2': {}, 'publishedDate': '', 'status': 'fixed in 3.1.0, 2.6.9'},
         'root_package_name': 'helmet', 'root_package_version': '2.3.0', 'root_package_fix_version': '2.4.0'},
        {'details': {'cveId': 'GHSA-C3M8-X3CG-QM2C', 'severity': 'medium', 'packageName': 'helmet-csp',
                     'packageVersion': '1.2.2', 'link': '', 'cvss': 4, 'vector': '',
                     'description': '',
                     'riskFactorsV2': {}, 'publishedDate': '', 'status': 'fixed in 2.9.1',
                     'rootPackageFixedVersion': '2.4.0'},
         'root_package_name': 'helmet', 'root_package_version': '2.3.0'},
        {'details': {'cveId': 'GHSA-C3M8-X3CG-QM2C', 'severity': 'medium', 'packageName': 'helmet',
                     'packageVersion': '2.3.0', 'link': '', 'cvss': 4, 'vector': '',
                     'description': '', 'riskFactorsV2': {}, 'publishedDate': '', 'status': 'fixed in 2.4.0'},
         'root_package_name': 'helmet', 'root_package_version': '2.3.0'},
        {'details': {'cveId': 'PRISMA-2021-0013', 'severity': 'medium', 'packageName': 'marked',
                     'packageVersion': '0.3.9',
                     'link': '', 'cvss': 0, 'vector': '',
                     'description': '',
                     'riskFactorsV2': {},
                     'publishedDate': '', 'status': 'fixed in 1.1.1'}, 'root_package_name': 'marked',
         'root_package_version': '0.3.9'},
        {'details': {'cveId': 'CVE-2022-21681', 'severity': 'high', 'packageName': 'marked', 'packageVersion': '0.3.9',
                     'link': '', 'cvss': 7.5,
                     'vector': '',
                     'description': '',
                     'riskFactorsV2': {},
                     'publishedDate': '', 'status': 'fixed in 4.0.10'}, 'root_package_name': 'marked',
         'root_package_version': '0.3.9'},
        {'details': {'cveId': 'CVE-2022-21680', 'severity': 'high', 'packageName': 'marked', 'packageVersion': '0.3.9',
                     'link': '', 'cvss': 7.5,
                     'vector': '',
                     'description': '',
                     'riskFactorsV2': {},
                     'publishedDate': '', 'status': 'fixed in 4.0.10'}, 'root_package_name': 'marked',
         'root_package_version': '0.3.9'},
        {'details': {'cveId': 'PRISMA-2022-0230', 'severity': 'high', 'packageName': 'mocha', 'packageVersion': '2.5.3',
                     'link': '', 'cvss': 7.5, 'vector': '',
                     'description': '',
                     'riskFactorsV2': {}, 'publishedDate': '', 'status': 'open'},
         'root_package_name': 'mocha', 'root_package_version': '2.5.3'},
        {'details': {'cveId': 'PRISMA-2022-0335', 'severity': 'medium', 'packageName': 'mocha',
                     'packageVersion': '2.5.3',
                     'link': '',
                     'cvss': 5.3, 'vector': '',
                     'description': '',
                     'riskFactorsV2': {}, 'publishedDate': '', 'status': 'open'},
         'root_package_name': 'mocha', 'root_package_version': '2.5.3'},
        {'details': {'cveId': 'GHSA-MH5C-679W-HH4R', 'severity': 'high', 'packageName': 'mongodb',
                     'packageVersion': '2.2.36',
                     'link': '', 'cvss': 7, 'vector': '', 'description': '',
                     'riskFactorsV2': {},
                     'publishedDate': '', 'status': 'fixed in 3.1.13'}, 'root_package_name': 'mongodb',
         'root_package_version': '2.2.36'},
        {'details': {'cveId': 'CVE-2019-2391', 'severity': 'medium', 'packageName': 'bson', 'packageVersion': '1.0.9',
                     'link': '', 'cvss': 4, 'vector': '', 'description': '',
                     'riskFactorsV2': {}, 'publishedDate': '', 'status': 'fixed in 1.1.4'
                     }, 'root_package_name': 'mongodb', 'root_package_version': '2.2.36'},
        {'details': {'cveId': 'CVE-2020-7610', 'severity': 'critical', 'packageName': 'bson', 'packageVersion': '1.0.9',
                     'link': '', 'cvss': 9.8,
                     'vector': '',
                     'description': '',
                     'riskFactorsV2': {}, 'publishedDate': '', 'status': 'fixed in 1.1.4'
                     }, 'root_package_name': 'mongodb', 'root_package_version': '2.2.36'},
        {'details': {'cveId': 'CVE-2020-7598', 'severity': 'medium', 'packageName': 'minimist',
                     'packageVersion': '0.0.10',
                     'link': '', 'cvss': 5.6, 'vector': '', 'description': '',
                     'riskFactorsV2': {},
                     'publishedDate': '', 'status': 'fixed in 1.2.2'}, 'root_package_name': 'swig',
         'root_package_version': '1.4.2'},
        {'details': {'cveId': 'CVE-2021-44906', 'severity': 'critical', 'packageName': 'minimist',
                     'packageVersion': '0.0.10',
                     'link': '', 'cvss': 9.8,
                     'vector': '',
                     'description': '',
                     'riskFactorsV2': {},
                     'publishedDate': '', 'status': 'fixed in 1.2.6'}, 'root_package_name': 'swig',
         'root_package_version': '1.4.2'},
        {'details': {'cveId': 'PRISMA-2021-0169', 'severity': 'medium', 'packageName': 'uglify-js',
                     'packageVersion': '2.4.24', 'link': '',
                     'cvss': 5.3, 'vector': '',
                     'description': '',
                     'riskFactorsV2': {},
                     'publishedDate': '', 'status': 'fixed in 3.14.3'}, 'root_package_name': 'swig',
         'root_package_version': '1.4.2'},
        {'details': {'cveId': 'CVE-2015-8858', 'severity': 'high', 'packageName': 'uglify-js',
                     'packageVersion': '2.4.24',
                     'link': '', 'cvss': 7,
                     'vector': '',
                     'description': '',
                     'riskFactorsV2': {}, 'publishedDate': '', 'status': 'fixed in 2.6.0'},
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
            "riskFactorsV2": {
                "Attack complexity": "low",
                "Attack vector": "network",
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
            "description": "Cross-site scripting (XSS) vulnerability in the dismissChangeRelatedObjectPopup function ...",
            "severity": "medium",
            "packageName": "django",
            "packageVersion": "1.2",
            "link": "https://nvd.nist.gov/vuln/detail/CVE-2016-6186",
            "riskFactorsV2": {
                "Attack complexity": "low",
                "Attack vector": "network",
            },
            "impactedVersions": ["<=1.8.13"],
            "publishedDate": "2016-08-05T17:59:00+02:00",
            "discoveredDate": "2016-08-05T15:59:00Z",
            "fixDate": "2016-08-05T17:59:00+02:00",
        },
    ]


def get_vulnerabilities_details_is_used_packages() -> List[Dict[str, Any]]:
    return [
        {
            "id": "CVE-FAKE-111",
            "status": "fixed in 3.0.1, 2.2.9, 1.11.27",
            "cvss": 9.8,
            "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
            "description": "Django before 1.11.27, 2.x before 2.2.9, and 3.x before 3.0.1 allows account takeover. ...",
            "severity": "critical",
            "packageName": "package1",
            "packageVersion": "1.1.1",
            "link": "https://nvd.nist.gov/vuln/detail/CVE-2019-19844",
            "riskFactorsV2": {
                "Attack complexity": "low",
                "Attack vector": "network",
                "IsUsed": False,
                "ReachableFunction": False,
            },
            "impactedVersions": ["<1.11.27"],
            "publishedDate": "2019-12-18T20:15:00+01:00",
            "discoveredDate": "2019-12-18T19:15:00Z",
            "fixDate": "2019-12-18T20:15:00+01:00",
        },
        {
            "id": "CVE-FAKE-222",
            "status": "fixed in 1.9.8, 1.8.14",
            "cvss": 6.1,
            "vector": "CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N",
            "description": "Cross-site scripting (XSS) vulnerability in the dismissChangeRelatedObjectPopup function ...",
            "severity": "medium",
            "packageName": "package2",
            "packageVersion": "2.2.2",
            "link": "https://nvd.nist.gov/vuln/detail/CVE-2016-6186",
            "riskFactorsV2": {
                "Attack complexity": "low",
                "Attack vector": "network",
                "IsUsed": True,
                "ReachableFunction": False,
            },
            "impactedVersions": ["<=1.8.13"],
            "publishedDate": "2016-08-05T17:59:00+02:00",
            "discoveredDate": "2016-08-05T15:59:00Z",
            "fixDate": "2016-08-05T17:59:00+02:00",
        },
        {
            "id": "CVE-FAKE-333",
            "status": "fixed in 1.9.8, 1.8.14",
            "cvss": 6.1,
            "vector": "CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N",
            "description": "Cross-site scripting (XSS) vulnerability in the dismissChangeRelatedObjectPopup function ...",
            "severity": "medium",
            "packageName": "package3",
            "packageVersion": "3.3.3",
            "link": "https://nvd.nist.gov/vuln/detail/CVE-2016-6186",
            "riskFactorsV2": {
                "Attack complexity": "low",
                "Attack vector": "network",
                "IsUsed": True,
                "ReachableFunction": True,
            },
            "impactedVersions": ["<=1.8.13"],
            "publishedDate": "2016-08-05T17:59:00+02:00",
            "discoveredDate": "2016-08-05T15:59:00Z",
            "fixDate": "2016-08-05T17:59:00+02:00",
        },
        {
            "id": "CVE-FAKE-444",
            "status": "fixed in 1.9.8, 1.8.14",
            "cvss": 6.1,
            "vector": "CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N",
            "description": "Cross-site scripting (XSS) vulnerability in the dismissChangeRelatedObjectPopup function ...",
            "severity": "medium",
            "packageName": "package4",
            "packageVersion": "4.4.4",
            "link": "https://nvd.nist.gov/vuln/detail/CVE-2016-6186",
            "riskFactorsV2": {
                "Attack complexity": "low",
                "Attack vector": "network",
                "IsUsed": False,
                "ReachableFunction": True,
            },
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
             'riskFactorsV2': {'Attack complexity': 'low', 'Attack vector': 'network'}, 'publishedDate': '2021-01-14T10:29:35Z'},
            {'cveId': 'CVE-2022-21681', 'status': 'fixed in 4.0.10', 'severity': 'high', 'packageName': 'marked',
             'packageVersion': '0.3.9', 'link': 'https://github.com/advisories/GHSA-5v2h-r2cx-5xgj', 'cvss': 7.5,
             'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H',
             'description': 'Marked is a markdown parser and compiler. Prior to version 4.0.10, the regular expression `inline.reflinkSearch` may cause catastrophic backtracking against some strings and lead to a denial of service (DoS). Anyone who runs untrusted markdown through a vulnerable version of marked and does not use a worker with a time limit may be affected. This issue is patched in version 4.0.10. As a workaround, avoid running untrusted markdown through marked or run marked on a worker thread and set a reasonable time limit to prevent draining resources.',
             'riskFactorsV2': {'Attack complexity': 'low', 'Attack vector': 'network'}, 'publishedDate': '2022-01-14T17:15:00Z'},
            {'cveId': 'CVE-2022-21680', 'status': 'fixed in 4.0.10', 'severity': 'high', 'packageName': 'marked',
             'packageVersion': '0.3.9', 'link': 'https://github.com/advisories/GHSA-rrrm-qjm4-v8hf', 'cvss': 7.5,
             'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H',
             'description': 'Marked is a markdown parser and compiler. Prior to version 4.0.10, the regular expression `block.def` may cause catastrophic backtracking against some strings and lead to a regular expression denial of service (ReDoS). Anyone who runs untrusted markdown through a vulnerable version of marked and does not use a worker with a time limit may be affected. This issue is patched in version 4.0.10. As a workaround, avoid running untrusted markdown through marked or run marked on a worker thread and set a reasonable time limit to prevent draining resources.',
             'riskFactorsV2': {'Attack complexity': 'low', 'Attack vector': 'network'}, 'publishedDate': '2022-01-14T17:15:00Z'}
            ]


def get_vulnerabilities_details_no_deps_is_used_packages() -> List[Dict[str, Any]]:
    return [{'cveId': 'PRISMA-2021-0013', 'status': 'fixed in 1.1.1', 'severity': 'medium', 'packageName': 'marked',
             'packageVersion': '0.3.9', 'link': None, 'cvss': None, 'vector': None,
             'description': 'marked package prior to 1.1.1 are vulnerable to  Regular Expression Denial of Service (ReDoS). The regex within src/rules.js file have multiple unused capture groups which could lead to a denial of service attack if user input is reachable.  Origin: https://github.com/markedjs/marked/commit/bd4f8c464befad2b304d51e33e89e567326e62e0',
             'riskFactorsV2': {'Attack complexity': 'low', 'Attack vector': 'network', 'IsUsed': 'True'}, 'publishedDate': '2021-01-14T10:29:35Z'},
            {'cveId': 'CVE-2022-21681', 'status': 'fixed in 4.0.10', 'severity': 'high', 'packageName': 'marked',
             'packageVersion': '0.3.9', 'link': 'https://github.com/advisories/GHSA-5v2h-r2cx-5xgj', 'cvss': 7.5,
             'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H',
             'description': 'Marked is a markdown parser and compiler. Prior to version 4.0.10, the regular expression `inline.reflinkSearch` may cause catastrophic backtracking against some strings and lead to a denial of service (DoS). Anyone who runs untrusted markdown through a vulnerable version of marked and does not use a worker with a time limit may be affected. This issue is patched in version 4.0.10. As a workaround, avoid running untrusted markdown through marked or run marked on a worker thread and set a reasonable time limit to prevent draining resources.',
             'riskFactorsV2': {'Attack complexity': 'low', 'Attack vector': 'network', 'IsUsed': 'True'}, 'publishedDate': '2022-01-14T17:15:00Z'},
            {'cveId': 'CVE-2022-21680', 'status': 'fixed in 4.0.10', 'severity': 'high', 'packageName': 'marked',
             'packageVersion': '0.3.9', 'link': 'https://github.com/advisories/GHSA-rrrm-qjm4-v8hf', 'cvss': 7.5,
             'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H',
             'description': 'Marked is a markdown parser and compiler. Prior to version 4.0.10, the regular expression `block.def` may cause catastrophic backtracking against some strings and lead to a regular expression denial of service (ReDoS). Anyone who runs untrusted markdown through a vulnerable version of marked and does not use a worker with a time limit may be affected. This issue is patched in version 4.0.10. As a workaround, avoid running untrusted markdown through marked or run marked on a worker thread and set a reasonable time limit to prevent draining resources.',
             'riskFactorsV2': {'Attack complexity': 'low', 'Attack vector': 'network'}, 'publishedDate': '2022-01-14T17:15:00Z'}
            ]


def create_cli_license_violations_table_wrapper(with_line_numbers: bool) -> str:
    file_path = "/requirements.txt"

    package_licenses_details_map = {
        "django@1.2": [
            {
                "package_name": "django",
                "package_version": "1.2",
                "license": "DUMMY_LICENSE",
                "status": "OPEN",
                "policy": "BC_LIC_1",
                "lines": [1, 2] if with_line_numbers else [0, 0]
            },
            {
                "package_name": "django",
                "package_version": "1.2",
                "license": "DUMMY_LICENSE2",
                "status": "OPEN",
                "policy": "BC_LIC_1",
                "lines": [1, 2] if with_line_numbers else [0, 0]
            },
        ],
        "django@1.12": [
            {
                "package_name": "django",
                "package_version": "1.12",
                "license": "DUMMY_LICENSE3",
                "status": "OPEN",
                "policy": "BC_LIC_1",
                "lines": [0, 0]
            },
        ],
        "flask@0.6": [
            {
                "package_name": "flask",
                "package_version": "0.6",
                "license": "DUMMY_LICENSE3",
                "status": "OPEN",
                "policy": "BC_LIC_1",
                "lines": [5, 6] if with_line_numbers else [0, 0]
            },
        ]
    }

    return create_cli_license_violations_table(
        file_path=file_path,
        package_licenses_details_map=package_licenses_details_map,
        lines_details_found=with_line_numbers
    )


def create_cli_output_wrapper(with_line_numbers: bool) -> str:
    # given
    rootless_file_path = "requirements.txt"
    file_abs_path = "/path/to/requirements.txt"
    check_class = "checkov.sca_package.scanner.Scanner"
    packages = {
        get_package_alias("django", "1.2"): {
            'package_registry': "https://registry.npmjs.org/",
            'is_private_registry': False,
            'lines': [1, 2] if with_line_numbers else [0, 0]
        },
        get_package_alias("flask", "0.6"): {
            'package_registry': "https://registry.npmjs.org/",
            'is_private_registry': False,
            'lines': [5, 6] if with_line_numbers else [0, 0]
        }
    }
    dummy_package = {'package_registry': "https://registry.npmjs.org/", 'is_private_registry': False}
    license_statuses = [
        {
            "package_name": "django",
            "package_version": "1.2",
            "license": "DUMMY_LICENSE",
            "status": "OPEN",
            "policy": "BC_LIC_1",
        },
        {
            "package_name": "django",
            "package_version": "1.2",
            "license": "DUMMY_LICENSE2",
            "status": "OPEN",
            "policy": "BC_LIC_1",
        },
        {
            "package_name": "django",
            "package_version": "1.12",
            "license": "DUMMY_LICENSE_3",
            "status": "OPEN",
            "policy": "BC_LIC_2"
        },
        {
            "package_name": "flask",
            "package_version": "0.6",
            "license": "DUMMY_OTHER_LICENSE",
            "status": "OPEN",
            "policy": "BC_LIC_1",
        }
    ]
    # when
    cves_records = [
        create_report_cve_record(
            rootless_file_path=rootless_file_path,
            file_abs_path=file_abs_path,
            check_class=check_class,
            vulnerability_details=details,
            licenses='Unknown',
            package=packages.get(get_package_alias(details["packageName"], details["packageVersion"]), dummy_package),
            root_package={'name': "django", 'version': "1.2", 'lines': [1, 2] if with_line_numbers else [0, 0]},
            used_private_registry=False
        )
        for details in get_vulnerabilities_details()
    ]
    license_records = [
        create_report_license_record(
            rootless_file_path=rootless_file_path,
            file_abs_path=file_abs_path,
            check_class=check_class,
            licenses_status=license_status,
            package=packages.get(get_package_alias(license_status["package_name"], license_status["package_version"]),
                                 dummy_package),
        )
        for license_status in license_statuses
    ]
    cli_output: str = create_cli_output(True, cves_records + license_records)
    return cli_output

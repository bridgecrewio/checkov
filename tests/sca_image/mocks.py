from __future__ import annotations

from typing import Dict, Any

from checkov.runner_filter import RunnerFilter
from checkov.sca_image.runner import Runner


def mock_scan(self: Runner, image_id: str, dockerfile_path: str, runner_filter: RunnerFilter | None = None) -> Dict[str, Any]:
    return dict(results=[{'id': 'sha256:973f3910e3465433dbc712f147f2ce15c42be69ccd558a13a3ec74127b4bd801',
                          'distro': 'Ubuntu 22.04.1 LTS', 'distroRelease': 'jammy', 'collections': ['All'],
                          'packages': [{'type': 'os', 'name': 'pcre2', 'version': '10.39-3build1'},
                                       {'type': 'os', 'name': 'libidn2', 'version': '2.3.2-2build1',
                                        'licenses': ['GPL-3+']},
                                       {'type': 'os', 'name': 'perl', 'version': '5.34.0-3ubuntu1',
                                        'licenses': ['GPL-1+ or Artistic']},
                                       {'type': 'os', 'name': 'bzip2', 'version': '1.0.8-5build1',
                                        'licenses': ['BSD-variant']}],
                          'complianceDistribution': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'total': 0},
                          'complianceScanPassed': True,
                          'vulnerabilities': [
             {'id': 'CVE-2020-16156', 'status': 'needed', 'cvss': 7.8,
             'vector': 'CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H',
             'description': 'CPAN 2.28 allows Signature Verification Bypass.', 'severity': 'medium',
             'packageName': 'perl', 'packageVersion': '5.34.0-3ubuntu1',
             'link': 'https://people.canonical.com/~ubuntu-security/cve/2020/CVE-2020-16156',
             'riskFactors': ['Attack complexity: low', 'Medium severity'], 'impactedVersions': ['*'],
             'publishedDate': '2021-12-13T20:15:00+02:00', 'discoveredDate': '2022-08-11T14:03:31+03:00'},
             {'id': 'CVE-2022-1587', 'status': 'needed', 'cvss': 9.1,
                                                       'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H',
                                                       'description': 'An out-of-bounds read vulnerability was discovered in the PCRE2 library in the get_recurse_data_length() function of the pcre2_jit_compile.c file. This issue affects recursions in JIT-compiled regular expressions caused by duplicate data transfers.',
                                                       'severity': 'low', 'packageName': 'pcre2',
                                                       'packageVersion': '10.39-3build1',
                                                       'link': 'https://people.canonical.com/~ubuntu-security/cve/2022/CVE-2022-1587',
                                                       'riskFactors': ['Recent vulnerability', 'Attack complexity: low',
                                                                       'Attack vector: network'],
                                                       'impactedVersions': ['*'],
                                                       'publishedDate': '2022-05-17T00:15:00+03:00',
                                                       'discoveredDate': '2022-08-11T14:03:31+03:00'},
             {'id': 'CVE-2022-1586', 'status': 'needed', 'cvss': 9.1,
             'vector': 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H',
             'description': 'An out-of-bounds read vulnerability was discovered in the PCRE2 library in the compile_xclass_matchingpath() function of the pcre2_jit_compile.c file. This involves a unicode property matching issue in JIT-compiled regular expressions. The issue occurs because the character was not fully read in case-less matching within JIT.',
             'severity': 'low', 'packageName': 'pcre2', 'packageVersion': '10.39-3build1',
             'link': 'https://people.canonical.com/~ubuntu-security/cve/2022/CVE-2022-1586',
             'riskFactors': ['Attack vector: network', 'Recent vulnerability', 'Attack complexity: low'],
             'impactedVersions': ['*'], 'publishedDate': '2022-05-17T00:15:00+03:00',
             'discoveredDate': '2022-08-11T14:03:31+03:00'}
                ],
                          'vulnerabilityDistribution': {'critical': 0, 'high': 0, 'medium': 2, 'low': 6, 'total': 8},
                          'vulnerabilityScanPassed': True}])

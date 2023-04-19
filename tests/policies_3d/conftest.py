from __future__ import annotations

from typing import Any

import pytest

from checkov.common.bridgecrew.severities import Severity, Severities, BcSeverities
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.policies_3d.record import Policy3dRecord


@pytest.fixture()
def k8s_record_1() -> Record:
    return Record(
        check_name='Check 1 title', check_result={'result': CheckResult.FAILED}, file_path='/dir_a/dir_b/file1.yaml',
        file_line_range=[1, 16], resource='Pod.default.testPod1', check_class='', bc_check_id='BC_K8S_1',
        code_block=[(1, 'apiVersion: v1\n'), (2, 'kind: Pod\n'), (3, 'metadata:\n'),
                    (4, '  name: 3d-policy-3\n'), (5, 'spec:\n'), (6, '  containers:\n'),
                    (7, '    - name: demo 1\n'), (8, '      image: ubuntu:latest\n'),
                    (9, '      securityContext:\n'), (10, '        runAsNonRoot: false\n'),
                    (11, '    - name: demo 2\n'), (12, '      image: ubuntu:latest\n'),
                    (13, '      securityContext:\n'), (14, '        runAsUser: 0\n'),
                    (15, '    - name: demo 3\n'), (16, '      image: ubuntu:latest\n')],
        file_abs_path='/root/dir_a/dir_b/file1.yaml', evaluations={}, check_id='', severity=Severities[BcSeverities.MEDIUM])


@pytest.fixture()
def k8s_record_2() -> Record:
    return Record(
        check_name='Check 2 title', check_result={'result': CheckResult.FAILED}, file_path='/dir_a/dir_b/file1.yaml',
        file_line_range=[1, 16], resource='Pod.default.testPod1', check_class='', bc_check_id='BC_K8S_2',
        code_block=[(1, 'apiVersion: v1\n'), (2, 'kind: Pod\n'), (3, 'metadata:\n'),
                    (4, '  name: 3d-policy-3\n'), (5, 'spec:\n'), (6, '  containers:\n'),
                    (7, '    - name: demo 1\n'), (8, '      image: ubuntu:latest\n'),
                    (9, '      securityContext:\n'), (10, '        runAsNonRoot: false\n'),
                    (11, '    - name: demo 2\n'), (12, '      image: ubuntu:latest\n'),
                    (13, '      securityContext:\n'), (14, '        runAsUser: 0\n'),
                    (15, '    - name: demo 3\n'), (16, '      image: ubuntu:latest\n')],
        file_abs_path='/root/dir_a/dir_b/file1.yaml', evaluations={}, check_id='', severity=Severities[BcSeverities.LOW])


@pytest.fixture()
def k8s_record_3() -> Record:
    return Record(
        check_name='Check 3 title', check_result={'result': CheckResult.FAILED}, file_path='/dir_a/dir_b/file2.yaml',
        file_line_range=[1, 16], resource='Pod.default.testPod2', check_class='', bc_check_id='BC_K8S_3',
        code_block=[(1, 'apiVersion: v1\n'), (2, 'kind: Pod\n'), (3, 'metadata:\n'),
                    (4, '  name: 3d-policy-3\n'), (5, 'spec:\n'), (6, '  containers:\n'),
                    (7, '    - name: demo 1\n'), (8, '      image: image-with-no-cves\n'),
                    (9, '      securityContext:\n'), (10, '        runAsNonRoot: false\n'),
                    (11, '    - name: demo 2\n'), (12, '      image: ubuntu:latest\n'),
                    (13, '      securityContext:\n'), (14, '        runAsUser: 0\n'),
                    (15, '    - name: demo 3\n'), (16, '      image: ubuntu:latest\n')],
        file_abs_path='/root/dir_a/dir_b/file2.yaml', evaluations={}, check_id='', severity=Severities[BcSeverities.HIGH])


@pytest.fixture()
def k8s_report(k8s_record_1, k8s_record_2, k8s_record_3) -> Report:
    report = Report(check_type='kubernetes')
    report.add_record(k8s_record_1)
    report.add_record(k8s_record_2)
    report.add_record(k8s_record_3)
    return report


@pytest.fixture()
def k8s_report_2(k8s_record_1, k8s_record_3) -> Report:
    report = Report(check_type='kubernetes')
    report.add_record(k8s_record_1)
    report.add_record(k8s_record_3)
    return report


@pytest.fixture()
def cve_1() -> dict[str, Any]:
    return {'cveId': 'CVE-2022-42898', 'status': 'fixed in 1.19.2-2ubuntu0.1', 'severity': 'medium',
                  'packageName': 'krb5', 'packageVersion': '1.19.2-2', 'dockerImageName': 'ubuntu:latest',
                  'link': 'https://people.canonical.com/~ubuntu-security/cve/2022/CVE-2022-42898',
                  'cvss': 8.8, 'vector': 'CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H',
                  'description': 'PAC parsing in MIT Kerberos 5 (aka krb5) before 1.19.4 ...',
                  'riskFactors': ['DoS', 'Has fix', 'Medium severity', 'Recent vulnerability',
                                  'Remote execution', 'Attack complexity: low', 'Attack vector: network'],
                  'publishedDate': '2022-12-25T06:15:00Z'}

@pytest.fixture()
def cve_2() -> dict[str, Any]:
    return {'cveId': 'CVE-2022-3821', 'status': 'needed', 'severity': 'medium',
              'packageName': 'systemd', 'packageVersion': '249.11-0ubuntu3.6', 'dockerImageName': 'ubuntu:latest',
              'link': 'https://people.canonical.com/~ubuntu-security/cve/2022/CVE-2022-3821',
              'cvss': 5.5, 'vector': 'CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H',
              'description': 'An off-by-one Error issue was discovered in Systemd in ...',
              'riskFactors': ['DoS', 'Medium severity', 'Recent vulnerability',
                              'Attack complexity: low'], 'publishedDate': '2022-11-08T22:15:00Z'}

@pytest.fixture()
def sca_image_cached_results(cve_1, cve_2) -> list[dict[str, Any]]:
    return [{'dockerImageName': 'ubuntu:latest', 'dockerFilePath': '/dir_a/dir_b/file1.yaml',
             'dockerFileContent': 'image: ubuntu:latest', 'type': 'Image',
             'sourceId': 'owner-name/repo-name', 'branch': 'branch-name', 'sourceType': 'cli',
             'relatedResourceId': '/root/dir_a/dir_b/file1.yaml:Pod.default.testPod1',
             'vulnerabilities': [cve_1, cve_2]}]


@pytest.fixture()
def sca_image_report(sca_image_cached_results) -> Report:
    report = Report(check_type='sca_image')
    report.image_cached_results = sca_image_cached_results
    return report


@pytest.fixture()
def scan_reports(k8s_report, sca_image_report) -> list[Report]:
    return [k8s_report, sca_image_report]

@pytest.fixture()
def scan_reports_2(k8s_report_2, sca_image_report) -> list[Report]:
    return [k8s_report_2, sca_image_report]


@pytest.fixture()
def policy_3d_1() -> dict[str, Any]:
    return {'id': 'CKV_P3D_1', 'title': '3d policy 1', 'guideline': 'guideline-1', 'severity': 'CRITICAL',
               'category': 'Policy3D', 'code': '{"iac":{"kubernetes":["BC_K8S_1"]},"cve":{"risk_factor":["DoS"]}}'}

@pytest.fixture()
def policy_3d_2() -> dict[str, Any]:
    return {'id': 'CKV_P3D_2', 'title': '3d policy 2', 'guideline': 'guideline-2', 'severity': 'CRITICAL',
               'category': 'Policy3D',
               'code': '{"iac":{"kubernetes":["BC_K8S_2"]},"cve":{"risk_factor":["Recent vulnerability"]}}'}

@pytest.fixture()
def policy_3d_3() -> dict[str, Any]:
    return {'id': 'CKV_P3D_3', 'title': '3d policy 3', 'guideline': 'guideline-3', 'severity': 'CRITICAL',
               'category': 'Policy3D',
               'code': '{"iac":{"kubernetes":["BC_K8S_1", "BC_K8S_2"]},"cve":{"risk_factor":["Recent vulnerability"]}}'}

@pytest.fixture
def raw_3d_policy():
  return {'id': 'BC_3D_500', 'title': 'title_500', 'guideline': 'guideline_500',
          'severity': 'CRITICAL', 'pcSeverity': 'CRITICAL', 'category': 'Policy3D',
          'code': """{
            "version": "v1",
            "definition": [
              {
                "cves": {
                  "or": [
                    {
                      "and": [
                        {
                          "risk_factor": "DoS"
                        },
                        {
                          "risk_factor": "Medium Severity"
                        }
                      ]
                    }
                  ]
                }
              },
              {
                "iac": {
                  "or": [
                    {
                      "violation_id": "BC_K8S_1"
                    },
                    {
                      "violation_id": "BC_K8S_23"
                    }
                  ]
                }
              }
            ]
          }"""
        }

@pytest.fixture()
def policy_3d_record_single_iac_single_cve(k8s_record_1, cve_1) -> Policy3dRecord:
    record = Policy3dRecord(
        bc_check_id='BC_P3D_1',
        check_id='BC_P3D_1',
        check_name='3d policy 1',
        check_result={'result': CheckResult.FAILED},
        code_block=[],
        evaluations=None,
        file_path='',
        file_abs_path='',
        resource='',
        check_class='',
        file_line_range=[-1, -1],
        iac_records=[k8s_record_1],
        vulnerabilities=[cve_1],
        severity=Severities[BcSeverities.LOW],
        composed_from_iac_records=[],
        composed_from_secrets_records=[],
        composed_from_cves=[]
    )
    record.set_guideline('https://docs.bridgecrew.io/docs/bc_p3d_1')
    return record

@pytest.fixture()
def policy_3d_record_multi_iac_multi_cve(k8s_record_1, k8s_record_2, k8s_record_3, cve_1, cve_2) -> Policy3dRecord:
    record = Policy3dRecord(
        bc_check_id='BC_P3D_1',
        check_id='BC_P3D_1',
        check_name='3d policy 1',
        check_result={'result': CheckResult.FAILED},
        code_block=[],
        evaluations=None,
        file_path='',
        file_abs_path='',
        resource='',
        check_class='',
        file_line_range=[-1, -1],
        iac_records=[k8s_record_1, k8s_record_2, k8s_record_3],
        vulnerabilities=[cve_1, cve_2],
        severity=Severities[BcSeverities.LOW],
        composed_from_iac_records=[],
        composed_from_secrets_records=[],
        composed_from_cves=[]
    )
    record.set_guideline('https://docs.bridgecrew.io/docs/bc_p3d_1')
    return record
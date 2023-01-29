import unittest

from checkov.common.bridgecrew.severities import Severities
from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.policies3d.runner import Policy3dRunner
from checkov.policies3d.checks_parser import Policy3dParser
from checkov.common.bridgecrew.integration_features.features.policies_3d_integration import Policies3DIntegration

k8s_record_1 = Record(check_name='', check_result={'result': CheckResult.FAILED}, file_path='/dir_a/dir_b/file1.yaml',
                      file_line_range=[1, 16], resource='Pod.default.testPod1', check_class='', bc_check_id='BC_K8S_1',
                      code_block=[(1, 'apiVersion: v1\n'), (2, 'kind: Pod\n'), (3, 'metadata:\n'),
                                  (4, '  name: 3d-policy-3\n'), (5, 'spec:\n'), (6, '  containers:\n'),
                                  (7, '    - name: demo 1\n'), (8, '      image: ubuntu:latest\n'),
                                  (9, '      securityContext:\n'), (10, '        runAsNonRoot: false\n'),
                                  (11, '    - name: demo 2\n'), (12, '      image: ubuntu:latest\n'),
                                  (13, '      securityContext:\n'), (14, '        runAsUser: 0\n'),
                                  (15, '    - name: demo 3\n'), (16, '      image: ubuntu:latest\n')],
                      file_abs_path='/root/dir_a/dir_b/file1.yaml', evaluations={}, check_id='')

k8s_record_2 = Record(check_name='', check_result={'result': CheckResult.FAILED}, file_path='/dir_a/dir_b/file1.yaml',
                      file_line_range=[1, 16], resource='Pod.default.testPod1', check_class='', bc_check_id='BC_K8S_2',
                      code_block=[(1, 'apiVersion: v1\n'), (2, 'kind: Pod\n'), (3, 'metadata:\n'),
                                  (4, '  name: 3d-policy-3\n'), (5, 'spec:\n'), (6, '  containers:\n'),
                                  (7, '    - name: demo 1\n'), (8, '      image: ubuntu:latest\n'),
                                  (9, '      securityContext:\n'), (10, '        runAsNonRoot: false\n'),
                                  (11, '    - name: demo 2\n'), (12, '      image: ubuntu:latest\n'),
                                  (13, '      securityContext:\n'), (14, '        runAsUser: 0\n'),
                                  (15, '    - name: demo 3\n'), (16, '      image: ubuntu:latest\n')],
                      file_abs_path='/root/dir_a/dir_b/file1.yaml', evaluations={}, check_id='')

k8s_record_3 = Record(check_name='', check_result={'result': CheckResult.FAILED}, file_path='/dir_a/dir_b/file2.yaml',
                      file_line_range=[1, 16], resource='Pod.default.testPod2', check_class='', bc_check_id='BC_K8S_3',
                      code_block=[(1, 'apiVersion: v1\n'), (2, 'kind: Pod\n'), (3, 'metadata:\n'),
                                  (4, '  name: 3d-policy-3\n'), (5, 'spec:\n'), (6, '  containers:\n'),
                                  (7, '    - name: demo 1\n'), (8, '      image: image-with-no-cves\n'),
                                  (9, '      securityContext:\n'), (10, '        runAsNonRoot: false\n'),
                                  (11, '    - name: demo 2\n'), (12, '      image: ubuntu:latest\n'),
                                  (13, '      securityContext:\n'), (14, '        runAsUser: 0\n'),
                                  (15, '    - name: demo 3\n'), (16, '      image: ubuntu:latest\n')],
                      file_abs_path='/root/dir_a/dir_b/file2.yaml', evaluations={}, check_id='')
k8s_report = Report(check_type='kubernetes')
k8s_report.add_record(k8s_record_1)
k8s_report.add_record(k8s_record_2)
k8s_report.add_record(k8s_record_3)

sca_image_cached_results =[{'dockerImageName': 'ubuntu:latest', 'dockerFilePath': '/dir_a/dir_b/file1.yaml',
                          'dockerFileContent': 'image: ubuntu:latest', 'type': 'Image',
                          'sourceId': 'owner-name/repo-name', 'branch': 'branch-name', 'sourceType': 'cli',
                          'relatedResourceId': '/root/dir_a/dir_b/file1.yaml:Pod.default.testPod1',
                          'vulnerabilities': [
                              {'cveId': 'CVE-2022-42898', 'status': 'fixed in 1.19.2-2ubuntu0.1', 'severity': 'medium',
                               'packageName': 'krb5', 'packageVersion': '1.19.2-2',
                               'link': 'https://people.canonical.com/~ubuntu-security/cve/2022/CVE-2022-42898',
                               'cvss': 8.8, 'vector': 'CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H',
                               'description': 'PAC parsing in MIT Kerberos 5 (aka krb5) before 1.19.4 ...',
                               'riskFactors': ['DoS', 'Has fix', 'Medium severity', 'Recent vulnerability',
                                               'Remote execution', 'Attack complexity: low', 'Attack vector: network'],
                               'publishedDate': '2022-12-25T06:15:00Z'},
                              {'cveId': 'CVE-2022-3821', 'status': 'needed', 'severity': 'medium',
                               'packageName': 'systemd', 'packageVersion': '249.11-0ubuntu3.6',
                               'link': 'https://people.canonical.com/~ubuntu-security/cve/2022/CVE-2022-3821',
                               'cvss': 5.5, 'vector': 'CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H',
                               'description': 'An off-by-one Error issue was discovered in Systemd in ...',
                               'riskFactors': ['DoS', 'Medium severity', 'Recent vulnerability',
                                               'Attack complexity: low'], 'publishedDate': '2022-11-08T22:15:00Z'}]}]
sca_image_report = Report(check_type='sca_image')
sca_image_report.image_cached_results = sca_image_cached_results

scan_reports = [k8s_report, sca_image_report]

policy_3d_1 = {'id': 'CKV_P3D_1', 'title': '3d policy 1', 'guideline': 'guideline-1', 'severity': 'CRITICAL',
               'category': 'Policy3D', 'code': '{"iac":{"kubernetes":["BC_K8S_1"]},"cve":{"risk_factors":["DoS"]}}'}

policy_3d_2 = {'id': 'CKV_P3D_2', 'title': '3d policy 2', 'guideline': 'guideline-2', 'severity': 'CRITICAL',
               'category': 'Policy3D', 'code': '{"iac":{"kubernetes":["BC_K8S_2"]},"cve":{"risk_factors":["Recent vulnerability"]}}'}

policy_3d_3 = {'id': 'CKV_P3D_3', 'title': '3d policy 3', 'guideline': 'guideline-3', 'severity': 'CRITICAL',
               'category': 'Policy3D', 'code': '{"iac":{"kubernetes":["BC_K8S_1", "BC_K8S_2"]},"cve":{"risk_factors":["Recent vulnerability"]}}'}

class TestRunnerValid(unittest.TestCase):

    def test_runner_single_policy(self):
        # given
        checks = []
        parser = Policy3dParser()
        policies = [policy_3d_1]
        for policy in policies:
            converted_check = Policies3DIntegration._convert_raw_check(policy)
            check = parser.parse_raw_check(converted_check)
            check.severity = Severities[policy['severity']]
            check.bc_id = check.id
            checks.append(check)

        # when
        report = Policy3dRunner().run(checks=checks, scan_reports=scan_reports)

        # then
        self.assertEqual(len(report.failed_checks), 1)
        self.assertEqual(len(report.parsing_errors), 0)
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.skipped_checks), 0)

    def test_runner_multi_policy(self):
        # given
        checks = []
        parser = Policy3dParser()
        policies = [policy_3d_1, policy_3d_2]
        for policy in policies:
            converted_check = Policies3DIntegration._convert_raw_check(policy)
            check = parser.parse_raw_check(converted_check)
            check.severity = Severities[policy['severity']]
            check.bc_id = check.id
            checks.append(check)

        # when
        report = Policy3dRunner().run(checks=checks, scan_reports=scan_reports)

        # then
        self.assertEqual(len(report.failed_checks), 2)
        self.assertEqual(len(report.parsing_errors), 0)
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.skipped_checks), 0)

    def test_runner_multi_iac_checks_policy(self):
        # given
        checks = []
        parser = Policy3dParser()
        policies = [policy_3d_3]
        for policy in policies:
            converted_check = Policies3DIntegration._convert_raw_check(policy)
            check = parser.parse_raw_check(converted_check)
            check.severity = Severities[policy['severity']]
            check.bc_id = check.id
            checks.append(check)

        # when
        report = Policy3dRunner().run(checks=checks, scan_reports=scan_reports)

        # then
        self.assertEqual(len(report.failed_checks), 1)
        self.assertEqual(len(report.parsing_errors), 0)
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.skipped_checks), 0)


if __name__ == "__main__":
    unittest.main()

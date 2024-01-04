import os
import unittest
from unittest.mock import patch

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.integration_features.features.vulnerabilities_integration import \
    VulnerabilitiesIntegration, NORMALIZE_PREFIX
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
from checkov.common.output.record import Record, SCA_PACKAGE_SCAN_CHECK_NAME
from checkov.common.output.report import Report
from checkov.common.sast.consts import SastLanguages
from checkov.sast.report import SastReport
from checkov.common.sast.report_types import Package, File, Function, PrismaReport


class TestVulnerabilitiesIntegration(unittest.TestCase):

    @patch.dict('os.environ', {'CKV_ENABLE_UPLOAD_SAST_IMPORTS':'True', 'CKV_ENABLE_SCA_INTEGRATE_SAST': 'True'})
    def test_full_enrich_cves(self):
        instance = BcPlatformIntegration()

        vul_integration = VulnerabilitiesIntegration(instance)

        cve1 = Record(check_id='CKV_CVE_2022_38778', check_name=SCA_PACKAGE_SCAN_CHECK_NAME, file_path='/package.json',
                      vulnerability_details={
                          'id': 'CVE-2022-38778', 'severity': 'medium', 'package_name': 'decode-uri-component',
                          'package_version': '0.2.0',
                          'risk_factors': {'Severity': 'Medium', 'HasFix': True, 'DoS': False,
                                           'AttackVector': 'network', 'AttackComplexity': 'low', 'IsUsed': False}
                      }, check_result=None, code_block=None, file_line_range=None, resource=None, evaluations=None,
                      check_class=None, file_abs_path='')
        cve2 = Record(check_id='CKV_CVE_2022_38778', check_name=SCA_PACKAGE_SCAN_CHECK_NAME, file_path='/package.json',
                      vulnerability_details={
                          'id': 'CVE-2022-11111', 'severity': 'medium', 'package_name': 'decode-uri-component',
                          'package_version': '0.2.0',
                          'risk_factors': {'Severity': 'Medium', 'HasFix': True, 'DoS': False,
                                           'AttackVector': 'network', 'AttackComplexity': 'low', 'IsUsed': False}
                      }, check_result=None, code_block=None, file_line_range=None, resource=None, evaluations=None,
                      check_class=None, file_abs_path='')
        cve3 = Record(check_id='CKV_CVE_2022_38778', check_name=SCA_PACKAGE_SCAN_CHECK_NAME,
                      file_path='/no_exists/package.json',
                      vulnerability_details={
                          'id': 'CVE-2022-22222', 'severity': 'medium', 'package_name': 'decode-uri-component',
                          'package_version': '0.2.0',
                          'risk_factors': {'Severity': 'Medium', 'HasFix': True, 'DoS': False,
                                           'AttackVector': 'network',
                                           'AttackComplexity': 'low', 'IsUsed': False}
                      }, check_result=None, code_block=None, file_line_range=None, resource=None, evaluations=None,
                      check_class=None, file_abs_path='')
        failed_checks: list[Record] = [cve1, cve2, cve3]
        sast_imports = {
                        '/innerFiles/code.js': {'all': ["bson", "decode-uri-component", "parse-path"]},
                        '/main.js': {'all': ["bson", "decode-uri-component", "parse-path"]}
                        }

        sca_report: Report = Report(check_type=CheckType.SCA_PACKAGE)
        sca_report.failed_checks = failed_checks
        sast_report: SastReport = SastReport(check_type=CheckType.SAST_JAVASCRIPT,
                                             language=SastLanguages.JAVASCRIPT, metadata=None,
                                             sast_report=PrismaReport(rule_match={}, errors={}, profiler={},
                                                                      run_metadata={}, imports={}, reachability_report={}))
        sast_report.sast_imports = sast_imports
        merged_reports = [sca_report, sast_report]

        vul_integration.merge_sca_and_sast_reports(merged_reports)

        self.assertTrue(cve1.vulnerability_details.get('risk_factors', {})['IsUsed'])
        self.assertTrue(cve2.vulnerability_details.get('risk_factors', {})['IsUsed'])
        self.assertFalse(cve3.vulnerability_details.get('risk_factors', {})['IsUsed'])

    @patch.dict('os.environ', {'CKV_ENABLE_UPLOAD_SAST_IMPORTS':'True', 'CKV_ENABLE_SCA_INTEGRATE_SAST': 'True'})
    def test_unsupported_sast_lang(self):
        instance = BcPlatformIntegration()

        vul_integration = VulnerabilitiesIntegration(instance)

        cve1 = Record(check_id='CKV_CVE_2022_38778', check_name=SCA_PACKAGE_SCAN_CHECK_NAME, file_path='/csproj',
                      vulnerability_details={
                          'id': 'CVE-2022-38778', 'severity': 'medium', 'package_name': 'decode-uri-component',
                          'package_version': '0.2.0',
                          'risk_factors': {'Severity': 'Medium', 'HasFix': True, 'DoS': False,
                                           'AttackVector': 'network', 'AttackComplexity': 'low', 'IsUsed': False}
                      }, check_result=None, code_block=None, file_line_range=None, resource=None, evaluations=None,
                      check_class=None, file_abs_path='')

        failed_checks: list[Record] = [cve1]
        sast_imports = {
            'Imports': {'/innerFiles/code.js': {'All': ["'bson'", "'decode-uri-component'", "'parse-path'"]},
                        '/main.js': {'All': ["'bson'", "'decode-uri-component'", "'parse-path'"]}}}

        sca_report: Report = Report(check_type=CheckType.SCA_PACKAGE)
        sca_report.failed_checks = failed_checks
        sast_report: SastReport = SastReport(check_type=CheckType.SAST_JAVASCRIPT,
                                             language=SastLanguages.JAVASCRIPT, metadata=None,
                                             sast_report=PrismaReport(rule_match={}, errors={}, profiler={},
                                                                      run_metadata={}, imports={}, reachability_report={}))
        sast_report.sast_imports = sast_imports
        merged_reports = [sca_report, sast_report]

        vul_integration.merge_sca_and_sast_reports(merged_reports)

        self.assertFalse(cve1.vulnerability_details.get('risk_factors', {})['IsUsed'])


    def test_compare_paths_same_level(self):
        instance = BcPlatformIntegration()
        vul_integration = VulnerabilitiesIntegration(instance)
        main_file = '/package.json';
        relative_file = '/main.js';
        is_relative = vul_integration.is_deeper_or_equal_level(main_file, relative_file)
        self.assertTrue(is_relative)

    def test_compare_paths_child_level(self):
        instance = BcPlatformIntegration()
        vul_integration = VulnerabilitiesIntegration(instance)
        main_file = '/package.json';
        relative_file = '/src/main.js';
        is_relative = vul_integration.is_deeper_or_equal_level(main_file, relative_file)
        self.assertTrue(is_relative)

    def test_compare_paths_parent_level(self):
        instance = BcPlatformIntegration()
        vul_integration = VulnerabilitiesIntegration(instance)
        main_file = '/src/package.json';
        relative_file = '/main.js';
        is_relative = vul_integration.is_deeper_or_equal_level(main_file, relative_file)
        self.assertFalse(is_relative)

    def test_compare_paths_relative_level(self):
        instance = BcPlatformIntegration()
        vul_integration = VulnerabilitiesIntegration(instance)
        main_file = '/package.json';
        relative_file = '../main.js';
        is_relative = vul_integration.is_deeper_or_equal_level(main_file, relative_file)
        self.assertFalse(is_relative)

    def test_compare_paths_valid_relative_level(self):
        instance = BcPlatformIntegration()
        vul_integration = VulnerabilitiesIntegration(instance)
        main_file = '/src2/../src/main.js';
        relative_file = '/src/package.json';
        is_relative = vul_integration.is_deeper_or_equal_level(main_file, relative_file)
        self.assertTrue(is_relative)

    def test_normalized_package_name_case_dot(self):
        instance = BcPlatformIntegration()
        vul_integration = VulnerabilitiesIntegration(instance)
        original = '../asdas/asdasd/asdasd/asd.txt'
        expected = f"{NORMALIZE_PREFIX}asd.txt"
        result = vul_integration.normalize_package_name(original)
        self.assertTrue(result, expected)

    def test_normalized_package_name_case_without_relative(self):
        instance = BcPlatformIntegration()
        vul_integration = VulnerabilitiesIntegration(instance)
        original = 'asdas/asdasd/asdasd/asd.txt'
        expected = f"{NORMALIZE_PREFIX}asdas/asdasd/asdasd/asd.txt"
        result = vul_integration.normalize_package_name(original)
        self.assertTrue(result, expected)

    def test_normalized_package_name_case_dot_in_name(self):
        instance = BcPlatformIntegration()
        vul_integration = VulnerabilitiesIntegration(instance)
        original = 'asd.txt'
        expected = f"{NORMALIZE_PREFIX}asd.txt"
        result = vul_integration.normalize_package_name(original)
        self.assertTrue(result, expected)

    def test_normalized_package_name_case_relative_package(self):
        instance = BcPlatformIntegration()
        vul_integration = VulnerabilitiesIntegration(instance)
        original = '../asdas/asdasd/asdasd/asd.txt'
        expected = f"{NORMALIZE_PREFIX}asd.txt"
        result = vul_integration.normalize_package_name(original)
        self.assertTrue(result, expected)

    def test_normalized_package_name_case_with_underscore(self):
        instance = BcPlatformIntegration()
        vul_integration = VulnerabilitiesIntegration(instance)
        original = 'asd2_asd'
        expected = f"{NORMALIZE_PREFIX}asd2asd"
        result = vul_integration.normalize_package_name(original)
        self.assertTrue(result, expected)

    def test_normalized_package_name_case_with_minus(self):
        instance = BcPlatformIntegration()
        vul_integration = VulnerabilitiesIntegration(instance)
        original = 'asd2-asd'
        expected = f"{NORMALIZE_PREFIX}asd2asd"
        result = vul_integration.normalize_package_name(original)
        self.assertTrue(result, expected)

    def test_normalized_package_name_case_simple(self):
        instance = BcPlatformIntegration()
        vul_integration = VulnerabilitiesIntegration(instance)
        original = 'asd'
        expected = f"{NORMALIZE_PREFIX}asd"
        result = vul_integration.normalize_package_name(original)
        self.assertTrue(result, expected)

    def test_create_reachable_cves_by_package_map(self):
        filtered_reachability_entries = [
            ('/index.js', File(packages={
                'axios': Package(alias='ax', functions=[
                    Function(name='trim', alias='hopa', line_number=4, code_block='hopa()', cve_id='cve-11')
                ]),
                'lodash': Package(alias='', functions=[
                    Function(name='template', alias='', line_number=1, code_block='template()', cve_id='cve-12'),
                    Function(name='toNumber', alias='', line_number=4, code_block='hopa()', cve_id='cve-13')
                ])
            }))
        ]
        instance = BcPlatformIntegration()
        vul_integration = VulnerabilitiesIntegration(instance)
        reachable_data_by_package_map = vul_integration.create_reachable_cves_by_package_map(filtered_reachability_entries)
        assert reachable_data_by_package_map == {
            'axios': {'cve-11'},
            'lodash': {'cve-12', 'cve-13'}
        }


if __name__ == '__main__':
    unittest.main()

import unittest

import os

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.integration_features.features.policy_metadata_integration import integration as metadata_integration
from checkov.common.bridgecrew.severities import BcSeverities, Severities
from checkov.secrets.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestRunnerValid(unittest.TestCase):

    def setUp(self) -> None:
        self.orig_metadata = metadata_integration.check_metadata

    def test_runner_failing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/cfn"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['secrets']))
        self.assertEqual(len(report.failed_checks), 2)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_sanity_check_secrets(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/sanity/secrets"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['secrets'], checks=['CKV_SECRET_6']))
        self.assertEqual(len(report.failed_checks), 6)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_fp_sanity_check_secrets_non_iac(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/sanity/iac_fp"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['secrets'], checks=['CKV_SECRET_6'], enable_secret_scan_all_files=True))
        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_fp_sanity_check_secrets_iac(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/sanity/non_iac_fp"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['secrets'], checks=['CKV_SECRET_6'], enable_secret_scan_all_files=True))
        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_sanity_check_non_secrets(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/sanity/non_secrets"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['secrets'], checks=['CKV_SECRET_6']))
        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_runner_honors_enforcement_rules(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/cfn"
        runner = Runner()
        filter = RunnerFilter(framework=['secrets'], use_enforcement_rules=True)
        # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
        # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
        filter.enforcement_rule_configs = {CheckType.SECRETS: Severities[BcSeverities.OFF]}
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=filter)
        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(len(report.parsing_errors), 0)
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.skipped_checks), 0)
        report.print_console()

    def test_runner_passing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/terraform"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['secrets']))
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.failed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_runner_tf_failing_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/terraform_failed"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['secrets']))
        self.assertEqual(2, len(report.failed_checks))
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(report.skipped_checks, [])
        report.print_console()

    def test_runner_tf_skip_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/terraform_skip"

        report = Runner().run(
            root_folder=valid_dir_path,
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework=['secrets'])
        )

        self.assertEqual(len(report.skipped_checks), 1)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(len(report.skipped_checks), 1)

        report.print_console()

    def test_runner_specific_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/cfn"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['secrets'], checks=['CKV_SECRET_2']))
        self.assertEqual(len(report.skipped_checks), 0)
        self.assertEqual(len(report.failed_checks), 1)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])

    def test_runner_wildcard_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/cfn"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['secrets'], checks=['CKV_SECRET*']))
        self.assertEqual(len(report.skipped_checks), 0)
        self.assertEqual(len(report.failed_checks), 2)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])

    def test_runner_skip_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/cfn"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['secrets'], skip_checks=['CKV_SECRET_2']))
        self.assertEqual(len(report.skipped_checks), 0)
        self.assertEqual(len(report.failed_checks), 1)
        self.assertEqual(report.failed_checks[0].check_id, 'CKV_SECRET_6')
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])

    def test_record_has_severity(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/cfn"

        metadata_integration.check_metadata = {
            'CKV_SECRET_2': {
                'severity': Severities[BcSeverities.LOW]
            }
        }

        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['secrets'], checks=['CKV_SECRET_2']))
        self.assertEqual(report.failed_checks[0].severity, Severities[BcSeverities.LOW])

    def test_runner_check_severity(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/cfn"

        metadata_integration.check_metadata = {
            'CKV_SECRET_2': {
                'severity': Severities[BcSeverities.LOW]
            },
            'CKV_SECRET_6': {
                'severity': Severities[BcSeverities.HIGH]
            }
        }

        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['secrets'], checks=['MEDIUM']))
        self.assertEqual(len(report.skipped_checks), 0)
        self.assertEqual(len(report.failed_checks), 1)
        self.assertEqual(report.failed_checks[0].check_id, 'CKV_SECRET_6')
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])

    def test_runner_skip_check_severity(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/cfn"

        metadata_integration.check_metadata = {
            'CKV_SECRET_2': {
                'severity': Severities[BcSeverities.LOW]
            },
            'CKV_SECRET_6': {
                'severity': Severities[BcSeverities.HIGH]
            }
        }

        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['secrets'], skip_checks=['MEDIUM']))
        self.assertEqual(len(report.skipped_checks), 0)
        self.assertEqual(len(report.failed_checks), 1)
        self.assertEqual(report.failed_checks[0].check_id, 'CKV_SECRET_6')
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])

    def test_runner_skip_check_wildcard(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/cfn"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['secrets'], skip_checks=['CKV_SECRET*']))
        self.assertEqual(len(report.skipped_checks), 0)
        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])

    def test_runner_multiple_files(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['secrets']))
        self.assertEqual(9, len(report.failed_checks))
        self.assertEqual(report.parsing_errors, [])
        self.assertEqual(report.passed_checks, [])
        self.assertEqual(len(report.skipped_checks), 1)

    def test_runner_bc_ids(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources"
        runner = Runner()
        # the other tests will implicitly test this value being None

        metadata_integration.check_metadata = {
            'CKV_SECRET_2': {
                'id': 'BC_GIT_2'
            }
        }

        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['secrets']))
        for fc in report.failed_checks:
            if fc.check_id == 'CKV_SECRET_2':
                self.assertEqual(fc.bc_check_id, 'BC_GIT_2')
            else:
                self.assertIsNone(fc.bc_check_id)

    def tearDown(self) -> None:
        metadata_integration.check_metadata = self.orig_metadata

    def test_runner_requested_file_type_only_ts(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path,
                            external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['secrets'],
                                                       block_list_secret_scan=['.py', 'Dockerfile', '.tf', '.yml'],
                                                       enable_secret_scan_all_files=True))
        self.assertEqual(len(report.failed_checks), 2)

    def test_runner_requested_file_type_only_py(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['secrets'], block_list_secret_scan=['.ts', 'Dockerfile', '.tf', '.yml'],
                                                       enable_secret_scan_all_files=True))
        self.assertEqual(len(report.failed_checks), 2)

    def test_runner_requested_file_type_only_yml(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['secrets'], block_list_secret_scan=['.py', 'Dockerfile', '.tf', '.ts'],
                                                       enable_secret_scan_all_files=True))
        self.assertEqual(len(report.failed_checks), 2)

    def test_runner_requested_file_type_only_tf(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['secrets'],
                                                       block_list_secret_scan=['.py', 'Dockerfile', '.ts', '.yml'],
                                                       enable_secret_scan_all_files=True))
        self.assertEqual(len(report.failed_checks), 3)

    def test_runner_requested_file_type_only_tf_yml(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['secrets'], block_list_secret_scan=['.py', 'Dockerfile', '.ts'],
                                                       enable_secret_scan_all_files=True))
        self.assertEqual(len(report.failed_checks), 5)

    def test_runner_requested_file_type_all(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['secrets'], enable_secret_scan_all_files=True))
        self.assertEqual(len(report.failed_checks), 13)

    def test_runner_requested_file_only_dockerfile(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['secrets'], block_list_secret_scan=['.py', '.tf', '.ts', '.yml'],
                                                       enable_secret_scan_all_files=True))
        self.assertEqual(len(report.failed_checks), 4)


    def test_runner_no_requested_file(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['secrets']))
        self.assertEqual(len(report.failed_checks), 9)

    def test_true_positive_py(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_file_path = current_dir + "/resources/file_type/test.py"
        runner = Runner()
        report = runner.run(root_folder=None, files=[valid_file_path], external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['secrets'], enable_secret_scan_all_files=True))
        self.assertEqual(len(report.failed_checks), 2)

    def test_no_false_positive_yml_2(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/cfn"
        valid_file_path = valid_dir_path + "/secret-no-false-positive.yml"
        runner = Runner()
        report = runner.run(root_folder=None, files=[valid_file_path], external_checks_dir=None,
                            runner_filter=RunnerFilter(framework=['secrets'],
                                                       enable_secret_scan_all_files=True))
        self.assertEqual(len(report.failed_checks), 0)

    def test_runner_entropy_source_files(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/test_entropy_source_files"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, runner_filter=RunnerFilter(framework=['secrets'],
                                                                                   enable_secret_scan_all_files=True))
        self.assertEqual(len(report.failed_checks), 2)
        for failed in report.failed_checks:
            if failed.check_id == 'CKV_SECRET_6':
                self.assertEqual(failed.file_line_range, [4, 5])
            elif failed.check_id == 'CKV_SECRET_4':
                self.assertEqual(failed.file_line_range, [6, 7])
            else:
                self.fail(f'Got a bad result: {failed}')

    def test_runner_omit_multiple_secrets_in_line(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/omit_multiple_secrets/test"
        runner = Runner()
        runner_filter = RunnerFilter(framework=['secrets'], enable_secret_scan_all_files=True)
        report = runner.run(root_folder=valid_dir_path, runner_filter=runner_filter)
        self.assertEqual(len(report.failed_checks), 2)
        assert report.failed_checks[0].code_block[0][1] == "export AWS_ACCESS_KEY_ID=AKIAI**********\\nexport CIRCLE='rk_liv**********'\n"
        assert report.failed_checks[1].code_block[0][1] == "export AWS_ACCESS_KEY_ID=AKIAI**********\\nexport CIRCLE='rk_liv**********'\n"
            

if __name__ == '__main__':
    unittest.main()

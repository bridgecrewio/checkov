import os
import unittest
import dpath.util
from checkov.terraform.runner import Runner
from checkov.terraform.context_parsers.registry import parser_registry


class TestRunnerValid(unittest.TestCase):

    def test_runner_valid_tf(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/example"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None)
        report_json = report.get_json()
        self.assertTrue(isinstance(report_json, str))
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suites())
        self.assertEqual(report.get_exit_code(soft_fail=False), 1)
        self.assertEqual(report.get_exit_code(soft_fail=True), 0)
        summary = report.get_summary()
        self.assertGreaterEqual(summary['passed'], 1)
        self.assertGreaterEqual(summary['failed'], 1)
        self.assertEqual(summary["parsing_errors"], 1)
        report.print_json()
        report.print_console()
        report.print_junit_xml()

    def test_runner_passing_valid_tf(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        passing_tf_dir_path = current_dir + "/resources/valid_tf_only_passed_checks"

        print("testing dir" + passing_tf_dir_path)
        runner = Runner()
        report = runner.run(root_folder=passing_tf_dir_path, external_checks_dir=None)
        report_json = report.get_json()
        self.assertTrue(isinstance(report_json, str))
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suites())
        # self.assertEqual(report.get_exit_code(), 0)
        summary = report.get_summary()
        self.assertGreaterEqual(summary['passed'], 1)
        self.assertEqual(summary['failed'], 0)
        self.assertEqual(summary["parsing_errors"], 0)

    def test_runner_specific_file(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        passing_tf_file_path = current_dir + "/resources/valid_tf_only_passed_checks/example.tf"

        runner = Runner()
        report = runner.run(root_folder=None, external_checks_dir=None, files=[passing_tf_file_path])
        report_json = report.get_json()
        self.assertTrue(isinstance(report_json, str))
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suites())
        # self.assertEqual(report.get_exit_code(), 0)
        summary = report.get_summary()
        self.assertGreaterEqual(summary['passed'], 1)
        self.assertEqual(summary['failed'], 0)
        self.assertEqual(summary["parsing_errors"], 0)

    def test_check_ids_dont_collide(self):
        runner = Runner()
        unique_checks = {}
        bad_checks = []
        for registry in list(runner.block_type_registries.values()):
            checks = [check for entity_type in list(registry.checks.values()) for check in entity_type]
            for check in checks:
                if check.id not in unique_checks:
                    unique_checks[check.id] = check
                elif check != unique_checks[check.id]:
                    # A single check can have multiple resource blocks it checks, which means it will show up multiple times in the registry
                    bad_checks.append(f'{check.id}: {check.name}')
                    print(f'{check.id}: {check.name}')
        self.assertEqual(len(bad_checks), 0)

    def test_no_missing_ids(self):
        runner = Runner()
        unique_checks = set()
        for registry in list(runner.block_type_registries.values()):
            checks = [check for entity_type in list(registry.checks.values()) for check in entity_type]
            for check in checks:
                unique_checks.add(check.id)
        aws_checks = list(filter(lambda check_id: '_AWS_' in check_id, unique_checks))
        for i in range(1, len(aws_checks)):
            self.assertIn(f'CKV_AWS_{i}', aws_checks, msg=f'The new AWS violation should have the ID "CKV_AWS_{i}"')

        gcp_checks = list(filter(lambda check_id: '_GCP_' in check_id, unique_checks))
        for i in range(1, len(gcp_checks)):
            self.assertIn(f'CKV_GCP_{i}', gcp_checks, msg=f'The new GCP violation should have the ID "CKV_GCP_{i}"')

        azure_checks = list(filter(lambda check_id: '_AZURE_' in check_id, unique_checks))
        for i in range(1, len(azure_checks)):
            self.assertIn(f'CKV_AZURE_{i}', azure_checks,
                          msg=f'The new GCP violation should have the ID "CKV_AZURE_{i}"')

    def test_evaluate_string_booleans(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/hcl_0.11"
        tf_file = f"{valid_dir_path}/main.tf"
        runner = Runner()
        runner.run(root_folder=valid_dir_path, external_checks_dir=None)
        runner.evaluate_string_booleans()
        print()
        self.assertEqual(
            dpath.get(runner.tf_definitions[tf_file], 'resource/0/aws_db_instance/test_db/apply_immediately/0'), True)
        self.assertEqual(
            dpath.get(runner.tf_definitions[tf_file], 'resource/0/aws_db_instance/test_db/backup_retention_period/0'),
            True)
        self.assertEqual(
            dpath.get(runner.tf_definitions[tf_file], 'resource/0/aws_db_instance/test_db/storage_encrypted/0'), False)
        self.assertEqual(dpath.get(runner.tf_definitions[tf_file], 'resource/0/aws_db_instance/test_db/multi_az/0'),
                         False)

    def tearDown(self):
        parser_registry.definitions_context = {}


if __name__ == '__main__':
    unittest.main()

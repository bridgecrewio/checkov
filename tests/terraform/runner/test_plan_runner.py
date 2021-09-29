import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.plan_runner import Runner


class TestRunnerValid(unittest.TestCase):

    def test_runner_two_checks_only(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan/tfplan.json"
        runner = Runner()
        checks_allowlist = ["CKV_AWS_21"]
        report = runner.run(
            root_folder=None,
            files=[valid_plan_path],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework="all", checks=checks_allowlist),
        )
        report_json = report.get_json()
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suites())
        self.assertEqual(report.get_exit_code(soft_fail=False), 1)
        self.assertEqual(report.get_exit_code(soft_fail=True), 0)

        for record in report.failed_checks:
            self.assertIn(record.check_id, checks_allowlist)
        self.assertEqual(report.get_summary()["failed"], 3)
        self.assertEqual(report.get_summary()["passed"], 3)

    def test_runner_child_modules(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan_with_child_modules/tfplan.json"
        runner = Runner()
        report = runner.run(
            root_folder=None,
            files=[valid_plan_path],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework="all"),
        )
        report_json = report.get_json()
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suites())
        self.assertEqual(report.get_exit_code(soft_fail=False), 1)
        self.assertEqual(report.get_exit_code(soft_fail=True), 0)

        self.assertEqual(report.get_summary()["failed"], 3)
        self.assertEqual(report.get_summary()["passed"], 4)

    def test_runner_nested_child_modules(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan_nested_child_modules/tfplan.json"
        runner = Runner()
        runner.graph_registry.checks = []
        report = runner.run(
            root_folder=None,
            files=[valid_plan_path],
            external_checks_dir=[current_dir + "/extra_yaml_checks"],
            runner_filter=RunnerFilter(framework="all"),
        )
        report_json = report.get_json()
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suites())
        self.assertEqual(report.get_exit_code(soft_fail=False), 1)
        self.assertEqual(report.get_exit_code(soft_fail=True), 0)

        self.assertEqual(report.get_summary()["failed"], 15)
        self.assertEqual(report.get_summary()["passed"], 0)

        failed_check_ids = set([c.check_id for c in report.failed_checks])
        expected_failed_check_ids = {
            "CKV_AWS_37",
            "CKV_AWS_38",
            "CKV_AWS_39",
            "CKV_AWS_58",
            "CUSTOM_GRAPH_AWS_1"
        }

        assert failed_check_ids == expected_failed_check_ids

    def test_runner_root_module_resources_no_values(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan_root_module_resources_no_values/tfplan.json"
        runner = Runner()
        runner.graph_registry.checks = []
        report = runner.run(
            root_folder=None,
            files=[valid_plan_path],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework="all"),
        )
        report_json = report.get_json()
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suites())
        self.assertEqual(report.get_exit_code(soft_fail=False), 1)
        self.assertEqual(report.get_exit_code(soft_fail=True), 0)

        # 4 checks fail on test data for single eks resource as of present
        # If more eks checks are added then this number will need to increase correspondingly to reflect
        # This reasoning holds for all current pass/fails in these tests
        self.assertEqual(report.get_summary()["failed"], 4)
        self.assertEqual(report.get_summary()["passed"], 0)

        failed_check_ids = set([c.check_id for c in report.failed_checks])
        expected_failed_check_ids = {
            "CKV_AWS_37",
            "CKV_AWS_38",
            "CKV_AWS_39",
            "CKV_AWS_58",
        }

        assert failed_check_ids == expected_failed_check_ids

    def test_runner_data_resource_partial_values(self):
        # In rare circumstances a data resource with partial values in the plan could cause false negatives
        # Often 'data' does not even appear in the *_modules[x].resouces field within planned_values and is not scanned as expected
        # It can occur when tf module B depends on tf module A
        # And tf module A creates a resource that is used in a data block in tf module B
        # So some values can be known but other are not at plan time
        # This can cause the data block resource to be scanned as if it were a managed resource which is not configured correctly
        # See 'Modes': https://www.terraform.io/docs/internals/json-format.html#values-representation
        # This test verifies that such a circumstance stops occurring
        # There is a EKS Managed Resource and a EKS Data Resource
        # The EKS Managed Resource should have 4 failures corresponding with EKS checks.
        # The EKS Data Resource should not be scanned. Previously this would cause 8 failures.
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan_data_resource_partial_values/tfplan.json"
        runner = Runner()
        report = runner.run(
            root_folder=None,
            files=[valid_plan_path],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework="all"),
        )
        report_json = report.get_json()
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suites())
        self.assertEqual(report.get_exit_code(soft_fail=False), 1)
        self.assertEqual(report.get_exit_code(soft_fail=True), 0)

        self.assertEqual(report.get_summary()["failed"], 4)
        self.assertEqual(report.get_summary()["passed"], 0)

        failed_check_ids = set([c.check_id for c in report.failed_checks])
        expected_failed_check_ids = {
            "CKV_AWS_37",
            "CKV_AWS_38",
            "CKV_AWS_39",
            "CKV_AWS_58",
        }

        assert failed_check_ids == expected_failed_check_ids

    def test_runner_root_dir(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        root_dir = current_dir + "/resources"
        runner = Runner()
        report = runner.run(
            root_folder=root_dir, files=None, external_checks_dir=None, runner_filter=RunnerFilter(framework="all")
        )
        report_json = report.get_json()
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suites())
        self.assertEqual(report.get_exit_code(soft_fail=False), 1)
        self.assertEqual(report.get_exit_code(soft_fail=True), 0)

        self.assertGreaterEqual(report.get_summary()["failed"], 82)
        self.assertGreaterEqual(report.get_summary()["passed"], 76)

        files_scanned = list(set(map(lambda rec: rec.file_path, report.failed_checks)))
        self.assertGreaterEqual(len(files_scanned), 6)

    def test_record_relative_path_with_relative_dir(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "resources", "plan")

        # this is the relative path to the directory to scan (what would actually get passed to the -d arg)
        dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')

        runner = Runner()
        checks_allowlist = ["CKV_AWS_20"]
        report = runner.run(
            root_folder=dir_rel_path,
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework="terraform", checks=checks_allowlist),
        )

        all_checks = report.failed_checks + report.passed_checks
        for record in all_checks:
            # The plan runner sets file_path to be relative from the CWD already, so this is easy
            self.assertEqual(record.repo_file_path, record.file_path.replace("\\", "/"))

    def test_record_relative_path_with_abs_dir(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "resources", "plan")

        dir_abs_path = os.path.abspath(scan_dir_path)

        runner = Runner()
        checks_allowlist = ["CKV_AWS_20"]
        report = runner.run(
            root_folder=dir_abs_path,
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework="terraform", checks=checks_allowlist),
        )

        all_checks = report.failed_checks + report.passed_checks
        for record in all_checks:
            # The plan runner sets file_path to be relative from the CWD already, so this is easy
            self.assertEqual(record.repo_file_path, record.file_path.replace("\\", "/"))

    def test_record_relative_path_with_relative_file(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "plan", "tfplan.json")

        # this is the relative path to the file to scan (what would actually get passed to the -f arg)
        file_rel_path = os.path.relpath(scan_file_path)

        runner = Runner()
        checks_allowlist = ["CKV_AWS_20"]
        report = runner.run(
            root_folder=None,
            external_checks_dir=None,
            files=[file_rel_path],
            runner_filter=RunnerFilter(framework="terraform", checks=checks_allowlist),
        )

        all_checks = report.failed_checks + report.passed_checks
        for record in all_checks:
            # The plan runner sets file_path to be relative from the CWD already, so this is easy
            self.assertEqual(record.repo_file_path, record.file_path.replace("\\", "/"))

    def test_record_relative_path_with_abs_file(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "plan", "tfplan.json")

        file_abs_path = os.path.abspath(scan_file_path)

        runner = Runner()
        checks_allowlist = ["CKV_AWS_20"]
        report = runner.run(
            root_folder=None,
            external_checks_dir=None,
            files=[file_abs_path],
            runner_filter=RunnerFilter(framework="terraform", checks=checks_allowlist),
        )

        all_checks = report.failed_checks + report.passed_checks
        for record in all_checks:
            # The plan runner sets file_path to be relative from the CWD already, so this is easy
            self.assertEqual(record.repo_file_path, record.file_path.replace("\\", "/"))

    def test_runner_unexpected_eks_node_group_remote_access(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/unexpected/eks_node_group_remote_access.json"
        runner = Runner()
        report = runner.run(
            root_folder=None,
            files=[valid_plan_path],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework="all"),
        )
        report_json = report.get_json()
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suites())
        self.assertEqual(report.get_exit_code(soft_fail=False), 0)
        self.assertEqual(report.get_exit_code(soft_fail=True), 0)

        self.assertEqual(report.get_summary()["failed"], 0)
        self.assertEqual(report.get_summary()["passed"], 1)

    def test_runner_with_resource_reference(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_plan_path = current_dir + "/resources/plan_with_resource_reference/tfplan.json"
        allowed_checks = ["CKV_AWS_84"]

        report = Runner().run(
            root_folder=None,
            files=[valid_plan_path],
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework="all", checks=allowed_checks),
        )

        report_json = report.get_json()
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suites())
        self.assertEqual(report.get_exit_code(soft_fail=False), 0)
        self.assertEqual(report.get_exit_code(soft_fail=True), 0)

        self.assertEqual(report.get_summary()["failed"], 0)
        self.assertEqual(report.get_summary()["passed"], 1)


if __name__ == "__main__":
    unittest.main()

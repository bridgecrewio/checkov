import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.EKSControlPlaneLogging import check
from checkov.terraform.runner import Runner
from checkov.common.models.enums import CheckResult


class TestEKSControlPlaneLogging(unittest.TestCase):
    def test_failure(self):
        resource_conf = {'name': ['testcluster'], 'enabled_cluster_log_types': [['api', 'audit']]}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_failure_empty(self):
        resource_conf = {'name': ['testcluster']}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_success(self):
        resource_conf = {'name': ['testcluster'], 'enabled_cluster_log_types': [['api', 'audit', 'authenticator', 'controllerManager', 'scheduler']]}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.PASSED, scan_result)

    def test_failure_not_enabled(self):
        resource_conf = {'name': ['testcluster'], 'enabled_cluster_log_types': []}

        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)

    def test_file(self):
        # given
        test_files_dir = Path(__file__).parent / "example_EKSControlPlaneLogging"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "aws_eks_cluster.fully_enabled",
            "aws_eks_cluster.fully_enabled_with_dynamic_block"
        }
        failing_resources = {
            "aws_eks_cluster.partially_enabled",
            "aws_eks_cluster.not_configured"
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], 2)
        self.assertEqual(summary["failed"], 2)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)



if __name__ == '__main__':
    unittest.main()

import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.kubernetes.DefaultServiceAccountBinding import check
from checkov.terraform.runner import Runner


class TestDefaultServiceAccountBinding(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_DefaultServiceAccountBinding"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "kubernetes_cluster_role_binding.pass",
            "kubernetes_role_binding.pass",
            "kubernetes_cluster_role_binding_v1.pass",
            "kubernetes_role_binding_v1.pass",
        }

        failing_resources = {
            "kubernetes_cluster_role_binding.fail",
            "kubernetes_role_binding.fail",
            "kubernetes_cluster_role_binding_v1.fail",
            "kubernetes_role_binding_v1.fail",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], 2 * 2)
        self.assertEqual(summary["failed"], 2 * 2)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()

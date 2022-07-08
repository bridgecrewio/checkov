import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.kubernetes.DefaultNamespace import check
from checkov.terraform.runner import Runner


class TestDefaultNamespace(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_DefaultNamespace"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "kubernetes_pod.pass",
            "kubernetes_deployment.pass",
            "kubernetes_daemonset.pass",
            "kubernetes_stateful_set.pass",
            "kubernetes_replication_controller.pass",
            "kubernetes_job.pass",
            "kubernetes_cron_job.pass",
            "kubernetes_service.pass",
            "kubernetes_secret.pass",
            "kubernetes_service_account.pass",
            "kubernetes_role_binding.pass",
            "kubernetes_config_map.pass",
            "kubernetes_ingress.pass",
        }

        failing_resources = {
            "kubernetes_pod.fail",
            "kubernetes_pod.fail2",
            "kubernetes_deployment.fail",
            "kubernetes_daemonset.fail",
            "kubernetes_stateful_set.fail",
            "kubernetes_replication_controller.fail",
            "kubernetes_job.fail",
            "kubernetes_cron_job.fail",
            "kubernetes_service.fail",
            "kubernetes_secret.fail",
            "kubernetes_service_account.fail",
            "kubernetes_role_binding.fail",
            "kubernetes_config_map.fail",
            "kubernetes_ingress.fail"
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], 13)
        self.assertEqual(summary["failed"], 14)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()

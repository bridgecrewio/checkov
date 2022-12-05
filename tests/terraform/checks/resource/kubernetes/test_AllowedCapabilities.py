import unittest
from pathlib import Path

from checkov.common.models.enums import CheckResult
from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.kubernetes.AllowedCapabilities import check
from checkov.terraform.runner import Runner


class TestAllowedCapabilities(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_AllowedCapabilities"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "kubernetes_pod.pass",
            "kubernetes_pod.pass2",
            "kubernetes_pod_v1.pass",
            "kubernetes_pod_v1.pass2",
            "kubernetes_deployment.pass",
            "kubernetes_deployment.pass2",
            "kubernetes_deployment_v1.pass",
            "kubernetes_deployment_v1.pass2",
        }

        failing_resources = {
            "kubernetes_pod.fail",
            "kubernetes_pod_v1.fail",
            "kubernetes_deployment.fail",
            "kubernetes_deployment_v1.fail",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], 4 * 2)
        self.assertEqual(summary["failed"], 2 * 2)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)

    def test_terraform_plan(self):
        resource_conf = {'spec': [{'template': [{'spec': [{'container': [{'security_context': [{'capabilities': [[]]}]}]}]}]}]}
        scan_result = check.scan_resource_conf(conf=resource_conf)
        assert scan_result == CheckResult.PASSED


if __name__ == '__main__':
    unittest.main()

import unittest
from pathlib import Path

from checkov.kubernetes.checks.resource.k8s.ApiServerAuthorizationModeNotAlwaysAllow import check
from checkov.kubernetes.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestApiServerAuthorizationModeNotAlwaysAllow(unittest.TestCase):
    def test_summary(self):
        # given
        test_files_dir = Path(__file__).parent / "example_ApiServerAuthorizationModeNotAlwaysAllow"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "Pod.kube-system.kube-apiserver-no-mode",
            "Pod.kube-system.kube-apiserver-no-allow",
        }
        failing_resources = {
            "Pod.kube-system.kube-apiserver-allow",
            "Pod.kube-system.kube-apiserver-extra-allow",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], 2)
        self.assertEqual(summary["failed"], 2)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()

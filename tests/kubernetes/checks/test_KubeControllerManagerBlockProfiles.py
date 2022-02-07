import unittest
from pathlib import Path

from checkov.kubernetes.checks.resource.k8s.KubeControllerManagerBlockProfiles import check
from checkov.kubernetes.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestKubeControllerManagerBlockProfiles(unittest.TestCase):
    def test_summary(self):
        # given
        test_files_dir = Path(__file__).parent / "example_KubeControllerManagerBlockProfiles"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "Pod.kube-system.kube-controller-manager-disabled",
        }
        failing_resources = {
            "Pod.kube-system.kube-controller-manager-default",
            "Pod.kube-system.kube-controller-manager-enabled",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(1, summary["passed"])
        self.assertEqual(2, summary["failed"])
        self.assertEqual(0, summary["skipped"])
        self.assertEqual(0, summary["parsing_errors"])

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()

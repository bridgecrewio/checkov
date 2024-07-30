import unittest
from pathlib import Path

from checkov.kubernetes.checks.resource.k8s.Seccomp import check
from checkov.kubernetes.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestSeccomp(unittest.TestCase):
    def test_summary(self):
        # given
        test_files_dir = Path(__file__).parent / "example_Seccomp"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()
        passed_resources = [check.resource for check in report.passed_checks]
        failed_resources = [check.resource for check in report.failed_checks]

        self.assertEqual(summary["passed"], 12)
        self.assertEqual(summary["failed"], 4)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        expected_passed_resources = [
            "CronJob.default.cronjob-passed",
            "CronJob.default.cronjob-passed2",
            "CronJob.default.cronjob-passed3",
            "CronJob.default.cronjob-securityContext-passed",
            "Deployment.default.seccomp-passed-deployment",
            "Deployment.default.seccomp-passed-metadata-annotations",
            "Pod.default.seccomp-passed-metadata-annotations-docker",
            "Pod.default.seccomp-passed-metadata-annotations-runtime",
            "Pod.default.seccomp-passed-security-context",
            "StatefulSet.default.RELEASE-NAME",
            "Pod.default.my-secure-pod",
            "Deployment.aws-dev.fdn-svc",
        ]
        expected_failed_resources = [
            "CronJob.default.cronjob-failed",
            "Deployment.infra.app-cert-manager",
            "Pod.default.seccomp-failed",
            "Pod.default.my-insecure-pod",
        ]
        self.assertCountEqual(expected_passed_resources, passed_resources)
        self.assertCountEqual(expected_failed_resources, failed_resources)


if __name__ == "__main__":
    unittest.main()

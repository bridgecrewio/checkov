import os
import unittest
from pathlib import Path

from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.kubernetes.checks.Seccomp import check
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

        self.assertEqual(summary["passed"], 7)
        self.assertEqual(summary["failed"], 2)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        expected_passed_resources = [
            "CronJob.cronjob-passed.default",
            "Deployment.seccomp-passed-deployment.default",
            "Deployment.seccomp-passed-metadata-annotations.default",
            "Pod.seccomp-passed-metadata-annotations-docker.default",
            "Pod.seccomp-passed-metadata-annotations-runtime.default",
            "Pod.seccomp-passed-security-context.default",
            "StatefulSet.RELEASE-NAME.default",
        ]
        expected_failed_resources = [
            "Deployment.app-cert-manager.infra",
            "Pod.seccomp-failed.default",
        ]
        self.assertCountEqual(expected_passed_resources, passed_resources)
        self.assertCountEqual(expected_failed_resources, failed_resources)


if __name__ == "__main__":
    unittest.main()

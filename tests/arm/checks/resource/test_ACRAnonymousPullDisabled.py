import unittest
from pathlib import Path

from checkov.arm.checks.resource.ACRAnonymousPullDisabled import check
from checkov.arm.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestACRAnonymousPullDisabled(unittest.TestCase):
    def test_summary(self):
        # given
        test_files_dir = Path(__file__).parent / "example_ACRAnonymousPullDisabled"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "Microsoft.ContainerRegistry/registries.pass",
            "Microsoft.ContainerRegistry/registries.pass2",
            "Microsoft.ContainerRegistry/registries.pass3",
            "Microsoft.ContainerRegistry/registries.pass4",
            "Microsoft.ContainerRegistry/registries.pass5",
            "Microsoft.ContainerRegistry/registries.pass6"
        }
        failing_resources = {
            "Microsoft.ContainerRegistry/registries.fail",
            "Microsoft.ContainerRegistry/registries.fail2"
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], len(failing_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()

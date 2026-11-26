import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from checkov.dockerfile.checks.RootUser import check
from checkov.dockerfile.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestRootUser(unittest.TestCase):
    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_RootUser"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {"/success/Dockerfile.USER"}
        failing_resources = {"/failure/Dockerfile.USER"}

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary["passed"], 1)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)

    def test_user_and_group(self):
        cases = {
            "0": False,
            "root:wheel": False,
            "root:1000": False,
            "0:wheel": False,
            "0:1000": False,
            "000:1000": False,
            "+0:1000": False,
            "-0:1000": False,
            "app:root": True,
            "1000:0": True,
            "rootless:wheel": True,
        }
        with TemporaryDirectory() as directory:
            dockerfile = Path(directory) / "Dockerfile"
            for user, passes in cases.items():
                with self.subTest(user=user):
                    dockerfile.write_text(f"FROM alpine\nUSER root\nUSER {user}\n", encoding="utf-8")
                    report = Runner().run(
                        root_folder=directory, runner_filter=RunnerFilter(checks=[check.id])
                    )
                    self.assertEqual(len(report.passed_checks), int(passes))
                    self.assertEqual(len(report.failed_checks), int(not passes))


if __name__ == "__main__":
    unittest.main()

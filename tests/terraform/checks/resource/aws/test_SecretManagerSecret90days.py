import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.SecretManagerSecret90days import check
from checkov.terraform.runner import Runner


class TestSecretManagerSecret90days(unittest.TestCase):
    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_SecretManagerSecret90days"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "aws_secretsmanager_secret_rotation.pass",
            "aws_secretsmanager_secret_rotation.pass_scheduled_hours",
            "aws_secretsmanager_secret_rotation.pass_scheduled_days",
            "aws_secretsmanager_secret_rotation.pass_scheduled_cron",
        }
        failing_resources = {
            "aws_secretsmanager_secret_rotation.fail",
            "aws_secretsmanager_secret_rotation.fail_2",
            "aws_secretsmanager_secret_rotation.fail_scheduled_days",
            #"aws_secretsmanager_secret_rotation.fail_scheduled_cron", # Will handle later
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        # self.assertEqual(summary["passed"], len(passing_resources))
        # self.assertEqual(summary["failed"], len(failing_resources))
        # self.assertEqual(summary["skipped"], 0)
        # self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()

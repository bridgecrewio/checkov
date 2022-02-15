import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.RDSHasSecurityGroup import check
from checkov.terraform.runner import Runner


class TestRDSHasSecurityGroup(unittest.TestCase):
    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_RDSHasSecurityGroup"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        failing_resources = {
            "aws_db_security_group.exists",
        }

        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()

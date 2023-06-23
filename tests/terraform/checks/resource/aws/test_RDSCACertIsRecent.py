import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.RDSCACertIsRecent import check
from checkov.terraform.runner import Runner


class TestRDSCACertIsRecent(unittest.TestCase):
    def test(self):
        test_files_dir = Path(__file__).parent / "example_RDSCACertIsRecent"

        report = Runner().run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "aws_db_instance.pass[\"rds-ca-rsa2048-g1\"]",
            "aws_db_instance.pass[\"rds-ca-rsa4096-g1\"]",
            "aws_db_instance.pass[\"rds-ca-ecc384-g1\"]",
        }
        failing_resources = {
            "aws_db_instance.fail",
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary["passed"], 3)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()

import os
import unittest

from checkov.cloudformation.checks.resource.aws.S3Encryption import check
from checkov.cloudformation.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestS3Versioning(unittest.TestCase):

    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/S3Templates"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        self.assertEqual(summary['passed'], 6)
        self.assertEqual(summary['failed'], 0)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

    def test_dsse_kms(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_S3EncryptionDsse"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "AWS::S3::Bucket.PassDsseKms",
            "AWS::S3::Bucket.PassKms",
            "AWS::S3::Bucket.PassAes256",
        }
        failing_resources = {
            "AWS::S3::Bucket.FailUnknownAlgorithm",
        }

        self.assertEqual(summary['passed'], 3)
        self.assertEqual(summary['failed'], 1)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)
        self.assertEqual(passing_resources, {c.resource for c in report.passed_checks})
        self.assertEqual(failing_resources, {c.resource for c in report.failed_checks})


if __name__ == '__main__':
    unittest.main()

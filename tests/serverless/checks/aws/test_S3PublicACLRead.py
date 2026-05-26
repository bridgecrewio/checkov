import os
import unittest
from unittest import mock

from checkov.cloudformation.checks.resource.aws.S3PublicACLRead import check
from checkov.serverless.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestS3PublicACLRead(unittest.TestCase):

    @mock.patch.dict(os.environ, {"CHECKOV_SERVERLESS_RESOLVE_VARS": "true"})
    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_S3PublicACLRead"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        self.assertEqual(summary['passed'], 2)
        self.assertEqual(summary['failed'], 1)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

        for failed_check in report.failed_checks:
            self.assertEqual(dict(sorted(failed_check.entity_tags.items())), {"RESOURCE": "lambda", "PUBLIC": "False"})

    @mock.patch.dict(os.environ, {"CHECKOV_SERVERLESS_RESOLVE_VARS": "true"})
    def test_inclusion(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_S3PublicACLRead/S3PublicACLRead-PASSED-incl"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        self.assertEqual(summary['passed'], 1)
        self.assertEqual(summary['failed'], 0)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

        for failed_check in report.failed_checks:
            self.assertEqual(dict(sorted(failed_check.entity_tags.items())), {"RESOURCE": "lambda", "PUBLIC": "False"})

if __name__ == '__main__':
    unittest.main()

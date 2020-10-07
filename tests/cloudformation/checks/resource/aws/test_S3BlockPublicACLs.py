import os
import unittest

from checkov.cloudformation.checks.resource.aws.S3BlockPublicACLs import check
from checkov.cloudformation.runner import Runner
from checkov.common.models.enums import CheckResult
from checkov.runner_filter import RunnerFilter


class TestS3BlockPublicACLs(unittest.TestCase):

    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/S3Templates"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        self.assertEqual(summary['passed'], 1)
        self.assertEqual(summary['failed'], 5)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

    def test_failure_auth_read(self):
        resource_conf = {
            "Type": "AWS::S3::Bucket",
            "Properties": {
                "AccessControl": "AuthenticatedRead"
            }
        }
        scan_result = check.scan_resource_conf(conf=resource_conf)
        self.assertEqual(CheckResult.FAILED, scan_result)


if __name__ == '__main__':
    unittest.main()

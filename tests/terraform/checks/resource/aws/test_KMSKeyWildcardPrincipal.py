import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.KMSKeyWildcardPrincipal import check
from checkov.terraform.runner import Runner


class TestKMSKeyWildcardPrincipal(unittest.TestCase):

    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_KMSKeyWildcardPrincipal"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'aws_kms_key.pass_0',
            'aws_kms_key.pass_1',
            'aws_kms_key.pass_2',
            'aws_kms_key.pass_3'
        }
        failing_resources = {
            'aws_kms_key.fail_0',
            'aws_kms_key.fail_1',
            'aws_kms_key.fail_2',
            'aws_kms_key.fail_3',
            'aws_kms_key.fail_4'
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)
        
        self.assertEqual(summary['passed'], 4)
        self.assertEqual(summary['failed'], 5)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)


if __name__ == '__main__':
    unittest.main()

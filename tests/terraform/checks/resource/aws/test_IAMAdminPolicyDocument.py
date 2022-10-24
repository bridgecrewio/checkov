import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.IAMAdminPolicyDocument import check
from checkov.terraform.runner import Runner


class TestIAMAdminPolicyDocument(unittest.TestCase):

    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_IAMAdminPolicyDocument"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'aws_iam_policy.pass1',
            'aws_iam_policy.pass2',
            'aws_ssoadmin_permission_set_inline_policy.pass1'
        }
        failing_resources = {
            'aws_iam_policy.fail1',
            'aws_iam_policy.fail2',
            'aws_iam_policy.fail3',
            'aws_iam_policy.fail4',
            'aws_ssoadmin_permission_set_inline_policy.fail1'
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary['passed'], 3)
        self.assertEqual(summary['failed'], 5)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()
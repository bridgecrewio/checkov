import unittest
import os

from checkov.terraform.checks.resource.gcp.GoogleKMSKeyIsPublic import check
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner


class TestGoogleKMSKeyIsPublic(unittest.TestCase):

    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_GoogleKMSKeyIsPublic"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'google_kms_crypto_key_iam_policy.pass',
            'google_kms_crypto_key_iam_policy.pass2',
            'google_kms_crypto_key_iam_policy.pass3',
            'google_kms_crypto_key_iam_binding.pass',
            'google_kms_crypto_key_iam_member.pass'
        }
        failing_resources = {
            'google_kms_crypto_key_iam_policy.fail',
            'google_kms_crypto_key_iam_policy.fail2',
            'google_kms_crypto_key_iam_binding.fail',
            'google_kms_crypto_key_iam_member.fail'
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary['passed'], len(passing_resources))
        self.assertEqual(summary['failed'], len(failing_resources))
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()

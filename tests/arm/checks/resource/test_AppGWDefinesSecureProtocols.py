import os
import unittest
from checkov.runner_filter import RunnerFilter
from checkov.arm.runner import Runner
from checkov.arm.checks.resource.AppGWDefinesSecureProtocols import check


class TestAppGWDefinesSecureProtocols(unittest.TestCase):

    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = os.path.join(current_dir, "example_AppGWDefinesSecureProtocols")
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'Microsoft.Network/applicationGateways.with_protocolversion_and_cipher_pass',
            'Microsoft.Network/applicationGateways.with_policyName_pass1'
        }
        failing_resources = {
            'Microsoft.Network/applicationGateways.without_sslPolicy_fail',
            'Microsoft.Network/applicationGateways.empty_sslPolicy_fail1',
            'Microsoft.Network/applicationGateways.with_protocolversion_and_cipher_fail2',
            'Microsoft.Network/applicationGateways.with_policyName_fail3',
        }
        skipped_resources = {}

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])


        self.assertEqual(summary['passed'], len(passing_resources))
        self.assertEqual(summary['failed'], len(failing_resources))
        self.assertEqual(summary['skipped'], len(skipped_resources))
        self.assertEqual(summary['parsing_errors'], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()

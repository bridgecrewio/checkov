import unittest
import os

from checkov.terraform.checks.resource.panos.NetworkIPsecProtocols import check
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner


class TestNetworkIPsecProtocols(unittest.TestCase):

    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_NetworkIPsecProtocols"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'panos_ipsec_crypto_profile.pass1',
            'panos_panorama_ipsec_crypto_profile.pass2',
            'panos_ipsec_crypto_profile.pass3',
            'panos_panorama_ipsec_crypto_profile.pass4',
        }
        failing_resources = {
            'panos_ipsec_crypto_profile.fail1',
            'panos_panorama_ipsec_crypto_profile.fail2',
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary['passed'], 4)
        self.assertEqual(summary['failed'], 2)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()

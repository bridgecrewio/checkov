import unittest
import os

from checkov.terraform.checks.resource.panos.NetworkIPsecAuthAlgorithms import check
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner


class NetworkIPsecAuthAlgorithms(unittest.TestCase):

    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_NetworkIPsecAuthAlgorithms"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'panos_ipsec_crypto_profile.pass1',
            'panos_panorama_ipsec_crypto_profile.pass2',
            'panos_ipsec_crypto_profile.pass3',
            'panos_panorama_ipsec_crypto_profile.pass4',
            'panos_ipsec_crypto_profile.pass5',
            'panos_panorama_ipsec_crypto_profile.pass6',
            'panos_ipsec_crypto_profile.pass7',
            'panos_panorama_ipsec_crypto_profile.pass8',
        }
        failing_resources = {
            'panos_ipsec_crypto_profile.fail1',
            'panos_ipsec_crypto_profile.fail2',
            'panos_ipsec_crypto_profile.fail3',
            'panos_panorama_ipsec_crypto_profile.fail4',
            'panos_panorama_ipsec_crypto_profile.fail5',
            'panos_panorama_ipsec_crypto_profile.fail6',
            'panos_ipsec_crypto_profile.fail7',
            'panos_ipsec_crypto_profile.fail8',
            'panos_panorama_ipsec_crypto_profile.fail9',
            'panos_panorama_ipsec_crypto_profile.fail10',
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary['passed'], 8)
        self.assertEqual(summary['failed'], 10)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()

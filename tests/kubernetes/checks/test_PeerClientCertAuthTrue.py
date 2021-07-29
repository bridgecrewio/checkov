import os
import unittest

from checkov.kubernetes.checks.PeerClientCertAuthTrue import check
from checkov.kubernetes.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestPeerClientCertAuthTrue(unittest.TestCase):

    def test_summary(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_PeerClientCertAuthTrue"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()
        self.assertEqual(1, summary['passed'])
        self.assertEqual(2, summary['failed'])
        for failed in report.failed_checks:
            self.assertIn("should-fail", failed.resource)
        for passed in report.passed_checks:
            self.assertIn("should-pass", passed.resource)


if __name__ == '__main__':
    unittest.main()

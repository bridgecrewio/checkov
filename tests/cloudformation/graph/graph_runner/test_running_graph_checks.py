import itertools
import os
import unittest
from checkov.cloudformation.runner import Runner


class TestRunningGraphChecks(unittest.TestCase):

    def test_runner(self):
        dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), f"resources")
        report = Runner().run(dir_path)
        assert any(
            check.check_id == "CKV2_AWS_24" for check in itertools.chain(report.failed_checks, report.passed_checks))
        assert any(
            check.check_id == "CKV2_AWS_25" for check in itertools.chain(report.failed_checks, report.passed_checks))
        assert any(
            check.check_id == "CKV2_AWS_26" for check in itertools.chain(report.failed_checks, report.passed_checks))


if __name__ == '__main__':
    unittest.main()

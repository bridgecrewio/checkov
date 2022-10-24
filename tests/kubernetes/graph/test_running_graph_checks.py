import itertools
import os
import unittest

import pytest

from checkov.kubernetes.runner import Runner

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class TestRunningGraphChecks(unittest.TestCase):
    @pytest.mark.skip("Graph checks not written yet for K8s")
    def test_runner(self):
        root_dir = os.path.realpath(os.path.join(TEST_DIRNAME, "../runner/resources"))
        report = Runner().run(root_dir)
        assert any(
            check.check_id == "CKV2_K8S_21" for check in itertools.chain(report.failed_checks, report.passed_checks))
        summary = report.get_summary()
        self.assertEqual(summary["passed"], 0)
        self.assertEqual(summary["failed"], 5)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)


if __name__ == '__main__':
    unittest.main()

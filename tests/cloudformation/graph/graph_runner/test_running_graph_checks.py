import itertools
import os
import unittest
from pathlib import Path

import pytest

from checkov.cloudformation.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestRunningGraphChecks(unittest.TestCase):

    @pytest.mark.skip("Graph checks have not been written yet for cloudformation")
    def test_runner(self):
        dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")
        report = Runner().run(dir_path)
        assert any(
            check.check_id == "CKV2_AWS_24" for check in itertools.chain(report.failed_checks, report.passed_checks))
        assert any(
            check.check_id == "CKV2_AWS_25" for check in itertools.chain(report.failed_checks, report.passed_checks))
        assert any(
            check.check_id == "CKV2_AWS_26" for check in itertools.chain(report.failed_checks, report.passed_checks))

    @pytest.mark.skip("Graph checks have not been written yet for cloudformation")
    def test_runner_sam(self):
        # given
        test_dir_path = Path(__file__).parent.parent / "graph_builder/resources/sam"

        # when
        report = Runner().run(root_folder=str(test_dir_path), runner_filter=RunnerFilter(checks=["CKV2_AWS_26"]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "AWS::Serverless::Function.Function1",
            "AWS::Serverless::Function.Function2",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}

        self.assertEqual(summary["passed"], 2)
        self.assertEqual(summary["failed"], 0)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)


if __name__ == '__main__':
    unittest.main()

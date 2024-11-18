import itertools
import os
import unittest
from pathlib import Path

import pytest

from checkov.cloudformation.runner import Runner
from checkov.common.checks_infra.checks_parser import GraphCheckParser
from checkov.common.checks_infra.registry import Registry
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

    def test_jsonpath_policy(self):
        test_dir_path = Path(__file__).parent / "resources" / "jsonpath_policy"
        check_dir = Path(__file__).parent / "external_graph_checks"

        test_check_registry = Registry(
            checks_dir=f'{check_dir}',
            parser=GraphCheckParser()
        )

        # when
        report = Runner(external_registries=[test_check_registry]).run(root_folder=str(test_dir_path),
                              runner_filter=RunnerFilter(checks=["CKV2_CFN_JSONPATH_POLICY"]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "AWS::MediaStore::Container.pass-str",
        }

        failing_resources = {
            "AWS::MediaStore::Container.fail-str",
            "AWS::MediaStore::Container.fail-dict",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}


        self.assertEqual(summary["passed"], 1)
        self.assertEqual(summary["failed"], 2)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()

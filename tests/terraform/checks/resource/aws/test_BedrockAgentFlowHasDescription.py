import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner


class TestBedrockAgentFlowHasDescription(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = os.path.dirname(os.path.realpath(__file__))

        # when
        report = Runner().run(
            root_folder=None,
            files=[os.path.join(test_files_dir, "example_BedrockAgentFlowHasDescription.tf")],
            runner_filter=RunnerFilter(checks=["CKV_AWS_393"]),
        )

        # then
        summary = report.get_summary()

        passing_resources = {
            "aws_bedrockagent_flow.pass",
        }
        failing_resources = {
            "aws_bedrockagent_flow.fail",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], 1)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()

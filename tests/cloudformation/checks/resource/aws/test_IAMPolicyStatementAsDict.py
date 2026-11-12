import os
import unittest

from checkov.cloudformation.checks.resource.aws.IAMWriteAccess import check
from checkov.cloudformation.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestIAMPolicyStatementAsDict(unittest.TestCase):
    """IAM grammar allows a PolicyDocument ``Statement`` to be a single object
    instead of a list. The cloudsplaining-backed checks (CKV_AWS_107-111) must
    still evaluate such policies rather than silently skipping them."""

    def test_single_object_statement_is_evaluated(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = os.path.join(current_dir, "IAMPolicyStatementAsDict")

        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))

        passing = {c.resource for c in report.passed_checks}
        failing = {c.resource for c in report.failed_checks}

        self.assertIn("AWS::IAM::Policy.DictStatementWrite", failing)
        self.assertIn("AWS::IAM::Policy.DictStatementScoped", passing)


if __name__ == "__main__":
    unittest.main()

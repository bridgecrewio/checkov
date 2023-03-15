import unittest
from pathlib import Path

from checkov.terraform.checks.resource.gcp.GoogleProjectBasicRole import check
from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner


class TestGoogleProjectBasicRole(unittest.TestCase):
    def test(self):
        test_files_dir = Path(__file__).parent / "example_GoogleProjectBasicRole"
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            'google_project_iam_member.other',
            'google_project_iam_binding.other',
        }
        failing_resources = {
            'google_project_iam_member.owner',
            'google_project_iam_member.editor',
            'google_project_iam_member.viewer',
            'google_project_iam_binding.owner',
            'google_project_iam_binding.editor',
            'google_project_iam_binding.viewer',
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary['passed'], len(passing_resources))
        self.assertEqual(summary['failed'], len(failing_resources))
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == '__main__':
    unittest.main()
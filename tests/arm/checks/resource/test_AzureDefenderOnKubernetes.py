import unittest
from pathlib import Path
from checkov.arm.checks.resource.AzureDefenderOnKubernetes import check
from checkov.arm.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestAzureDefenderOnKubernetes(unittest.TestCase):
    def test_summary(self):
        # given
        test_files_dir = Path(__file__).parent / "example_AzureDefenderOnKubernetes"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        self.assertEqual(summary['passed'], 3)
        self.assertEqual(summary['failed'], 2)
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)


if __name__ == "__main__":
    unittest.main()

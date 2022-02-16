import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.data.external.ExternalData import check
from checkov.terraform.runner import Runner


class TestExternalData(unittest.TestCase):
    def test(self):
        test_files_dir = Path(__file__).parent / "example_external_data"

        report = Runner().run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()


        self.assertEqual(summary["passed"], 0)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)




if __name__ == "__main__":
    unittest.main()

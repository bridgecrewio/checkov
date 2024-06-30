import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner


class TestStorageAccountsTransportEncryption(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "a example skip"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[]))

        # then
        summary = report.get_summary()

        self.assertEqual(summary["passed"], 4)
        self.assertEqual(summary["failed"], 0)
        self.assertEqual(summary["skipped"], 10)
        self.assertEqual(summary["parsing_errors"], 0)


if __name__ == "__main__":
    unittest.main()

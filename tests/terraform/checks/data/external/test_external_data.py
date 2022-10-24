import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.runner import Runner
from checkov.terraform.checks.data.registry import data_registry

class TestExternalData(unittest.TestCase):
    def test(self):
        test_files_dir = Path(__file__).parent / "example_external_data"
        external_check_dir = Path(__file__).parent / "external_check"

        runner = Runner()
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=["CKV_TF_DATA_EXTERNAL_1"]),
                            external_checks_dir=[external_check_dir])
        summary = report.get_summary()
        print(data_registry)
        self.assertEqual(summary["passed"], 0)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)
        check = next(c for c in data_registry.checks["external"] if c.id == "CKV_TF_DATA_EXTERNAL_1")
        data_registry.checks["external"].remove(check)


if __name__ == "__main__":
    unittest.main()

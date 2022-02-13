import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.data.aws.IAMWriteAccess import check
from checkov.terraform.runner import Runner


class TestModuleCheck(unittest.TestCase):

    def test(self):
        external_checks = Path.joinpath(Path(__file__).parent , "example_external_dir_with_module_version_check/extra_checks").as_posix()
        test_files_dir = Path(__file__).parent / "resources"

        report = Runner().run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=["CKV_TF_MODULE_1"]),external_checks_dir=[external_checks])
        summary = report.get_summary()


        self.assertEqual(summary["passed"], 1)
        self.assertEqual(summary["failed"], 2)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)



if __name__ == "__main__":
    unittest.main()

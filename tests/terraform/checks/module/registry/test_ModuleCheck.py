import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.module.registry import module_registry
from checkov.terraform.runner import Runner


class TestModuleCheck(unittest.TestCase):
    def test_module_version(self):
        external_checks = Path.joinpath(Path(__file__).parent,
                                        "example_external_dir_with_module_version_check/extra_checks").as_posix()
        test_files_dir = Path(__file__).parent / "resources"

        report = Runner().run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=["CKV_TF_MODULE_1"]),
                              external_checks_dir=[external_checks])
        summary = report.get_summary()

        self.assertEqual(summary["passed"], 2)
        self.assertEqual(summary["failed"], 3)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        # remove custom checks
        check = next(c for c in module_registry.checks["module"] if c.id == "CKV_TF_MODULE_1")
        module_registry.checks["module"].remove(check)
        check = next(c for c in module_registry.checks["module"] if c.id == "CKV_TF_MODULE_2")
        module_registry.checks["module"].remove(check)

    def test_immutable_module(self):
        external_checks = Path.joinpath(Path(__file__).parent,
                                        "example_external_dir_with_module_version_check/extra_checks").as_posix()
        test_files_dir = Path(__file__).parent / "resources"

        report = Runner().run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=["CKV_TF_MODULE_2"]),
                              external_checks_dir=[external_checks])
        summary = report.get_summary()

        self.assertEqual(summary["passed"], 1)
        self.assertEqual(summary["failed"], 4)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        # remove custom checks
        check = next(c for c in module_registry.checks["module"] if c.id == "CKV_TF_MODULE_1")
        module_registry.checks["module"].remove(check)
        check = next(c for c in module_registry.checks["module"] if c.id == "CKV_TF_MODULE_2")
        module_registry.checks["module"].remove(check)


if __name__ == "__main__":
    unittest.main()

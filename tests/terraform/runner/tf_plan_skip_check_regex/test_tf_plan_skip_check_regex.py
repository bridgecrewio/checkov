import os
import unittest

from checkov.terraform.plan_runner import Runner
from checkov.runner_filter import RunnerFilter


class TestTFplanSkipCheckRegex(unittest.TestCase):

    def test_skip_all_checks(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = current_dir + "/resource"
        report = runner.run(
            root_folder=test_files_dir,
            runner_filter=RunnerFilter(skip_checks=[
                "CKV_AWS_*:.*.json$",
                "CKV2_AWS_*:.*.json$",
                "CKV_NCP_*:.*.json$",
                "CKV_AZURE_*:.*.json$",
                "CKV2_AZURE_*:.*.json$",
                "CKV2_GCP_*:.*.json$",
                "CKV_ADO_*:.*.json$",
                "CKV2_ADO_*:.*.json$",
                "CKV_OCI_*:.*.json$",
                "CKV2_OCI_*:.*.json$",
                "CKV_GIT_*:.*.json$",
                "CKV2_GIT_1:.*.json$"
            ])
        )
        summary = report.get_summary()

        self.assertEqual(summary['passed'], 0)
        self.assertEqual(summary['failed'], 0)
        # As skip is not being inserted to result in base check scan
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)

    def test_skip_some_checks(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = current_dir + "/resource"
        report1 = runner.run(
            root_folder=test_files_dir,
            runner_filter=RunnerFilter(skip_checks=["CKV2_AWS_*:.*.json$"])
        )
        summary1 = report1.get_summary()

        report2 = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter())
        summary2 = report2.get_summary()

        self.assertNotEqual(summary1['passed'], summary2['passed'])
        self.assertNotEqual(summary1['failed'], summary2['failed'])

    def test_skip_only_one_file(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = current_dir + "/resource"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(skip_checks=[
                "CKV_AWS_*:.*skip_directory.*.json$",
                "CKV2_AWS_*:.*skip_directory.*.json$",
                "CKV_NCP_*:.*skip_directory.*.json$",
                "CKV_AZURE_*:.*skip_directory.*.json$",
                "CKV2_AZURE_*:.*skip_directory.*.json$",
                "CKV2_GCP_*:.*skip_directory.*.json$",
                "CKV_ADO_*:.*skip_directory.*.json$",
                "CKV2_ADO_*:.*skip_directory.*.json$",
                "CKV_OCI_*:.*skip_directory.*.json$",
                "CKV2_OCI_*:.*skip_directory.*.json$",
                "CKV_GIT_*:.*skip_directory.*.json$",
                "CKV2_GIT_1:.*skip_directory.*.json$"
            ]))

        summary = report.get_summary()
        no_skip_report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter())
        no_skip_summary = no_skip_report.get_summary()
        self.assertNotEqual(summary['passed'], no_skip_summary['passed'])
        self.assertNotEqual(summary['failed'], no_skip_summary['failed'])


if __name__ == '__main__':
    unittest.main()

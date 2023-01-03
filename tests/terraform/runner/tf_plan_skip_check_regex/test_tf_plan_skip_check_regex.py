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
                "CKV_AZURE_*:.*.json",
                "CKV2_AZURE_*:.*.json",
                "CKV2_GCP_*:.*.json",
                "CKV_ADO_*:.*.json",
                "CKV2_ADO_*:.*.json",
                "CKV_OCI_*:.*.json",
                "CKV_GIT_*:.*.json",
                "CKV2_GIT_1:.*.json",
            ])
        )
        summary = report.get_summary()

        self.assertEqual(summary['passed'], 0)
        self.assertEqual(summary['failed'], 0)
        # As skip is not being inserted to result in base check scan
        self.assertEqual(summary['skipped'], 0)
        self.assertEqual(summary['parsing_errors'], 0)


if __name__ == '__main__':
    unittest.main()

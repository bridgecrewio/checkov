import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.yandexcloud.IAMPassportAccountUsage import scanner
from checkov.terraform.runner import Runner

class TestIAMPassportAccountUsage(unittest.TestCase):
    def test(self):
        test_files_dir = Path(__file__).parent / "example_IAMPassportAccountUsage"
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[scanner.id]))
        summary = report.get_summary()

        passing_resources = {
            "yandex_resourcemanager_folder_iam_binding.pass",
            "yandex_resourcemanager_folder_iam_member.pass",
            "yandex_resourcemanager_cloud_iam_binding.pass",
            "yandex_resourcemanager_cloud_iam_member.pass",
            "yandex_organizationmanager_organization_iam_binding.pass",
            "yandex_organizationmanager_organization_iam_member.pass"
        }
        failing_resources = {
            "yandex_resourcemanager_folder_iam_binding.fail",
            "yandex_resourcemanager_folder_iam_member.fail",
            "yandex_resourcemanager_cloud_iam_binding.fail",
            "yandex_resourcemanager_cloud_iam_member.fail",
            "yandex_organizationmanager_organization_iam_binding.fail",
            "yandex_organizationmanager_organization_iam_member.fail"
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], 6)
        self.assertEqual(summary["failed"], 6)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)

if __name__ == "__main__":
    unittest.main()

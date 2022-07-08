import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.yandexcloud.IAMOrganizationElevatedMembers import check
from checkov.terraform.runner import Runner

class TestIAMOrganizationElevatedMembers(unittest.TestCase):
    def test(self):
        test_files_dir = Path(__file__).parent / "example_IAMOrganizationElevatedMembers"
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "yandex_organizationmanager_organization_iam_binding.pass-1",
            "yandex_organizationmanager_organization_iam_member.pass-2"
        }
        failing_resources = {
            "yandex_organizationmanager_organization_iam_binding.fail-1",
            "yandex_organizationmanager_organization_iam_binding.fail-2",
            "yandex_organizationmanager_organization_iam_binding.fail-3",
            "yandex_organizationmanager_organization_iam_member.fail-4",
            "yandex_organizationmanager_organization_iam_member.fail-5",
            "yandex_organizationmanager_organization_iam_member.fail-6"
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], 2)
        self.assertEqual(summary["failed"], 6)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)

if __name__ == "__main__":
    unittest.main()

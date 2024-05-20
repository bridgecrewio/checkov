import unittest
from checkov.arm.checks.resource.AKSLocalAdminDisabled import check
from pathlib import Path
from checkov.arm.runner import Runner
from checkov.runner_filter import RunnerFilter


class TestAKSLocalAdminDisabled(unittest.TestCase):
    def test_summary(self):
        test_files_dir = Path(__file__).parent / "example_AKSLocalAdminDisabled"
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()
        print(f"\nSummary: {summary}")

        # Debugging: Print out actual resources reported by Checkov
        print("Actual passed resources:")
        for resource in report.passed_checks:
            print(resource.resource)

        passing_resources = {
            "Microsoft.ContainerService/managedClusters.pass",
        }

        failing_resources = {
            "Microsoft.ContainerService/managedClusters.fail",
            "Microsoft.ContainerService/managedClusters.fail2"
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], len(failing_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        print(f"Passed check resources: {passed_check_resources}")
        print(f"Failed check resources: {failed_check_resources}")

        self.assertSetEqual(passing_resources, passed_check_resources)
        self.assertSetEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()

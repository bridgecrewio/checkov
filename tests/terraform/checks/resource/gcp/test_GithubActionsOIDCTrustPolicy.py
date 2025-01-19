import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.gcp.GithubActionsOIDCTrustPolicy import check
from checkov.terraform.runner import Runner


class TestGithubActionsOIDCTrustPolicy(unittest.TestCase):
    def test(self):
        test_files_dir = Path(__file__).parent / "example_GithubActionsOIDCTrustPolicy"

        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "google_iam_workload_identity_pool_provider.pass1",
            "google_iam_workload_identity_pool_provider.pass2",
            "google_iam_workload_identity_pool_provider.pass3",
            "google_iam_workload_identity_pool_provider.pass_org_only",
        }
        failing_resources = {
            "google_iam_workload_identity_pool_provider.fail1",
            "google_iam_workload_identity_pool_provider.fail2",
            "google_iam_workload_identity_pool_provider.fail_wildcard",
            "google_iam_workload_identity_pool_provider.fail_abusable",
            "google_iam_workload_identity_pool_provider.fail_wildcard_assertion",
            "google_iam_workload_identity_pool_provider.fail_misused_repo",
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        print("\nPassed resources:", sorted(list(passed_check_resources)))
        print("Expected passing:", sorted(list(passing_resources)))
        print("\nFailed resources:", sorted(list(failed_check_resources)))
        print("Expected failing:", sorted(list(failing_resources)))

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], len(failing_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()

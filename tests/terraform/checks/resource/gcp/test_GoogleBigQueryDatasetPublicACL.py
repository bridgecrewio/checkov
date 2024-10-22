import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.gcp.GoogleBigQueryDatasetPublicACL import check
from checkov.terraform.runner import Runner


class TestGoogleBigQueryDatasetPublicACL(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_GoogleBigQueryDatasetPublicACL"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "google_bigquery_dataset.pass_special_group",
            "google_bigquery_dataset.pass_user_by_email",
            "google_bigquery_dataset.pass_group_by_email",
            "google_bigquery_dataset.pass_domain",
            "google_bigquery_dataset.pass_view",
            "google_bigquery_dataset.pass_routine",
            "google_bigquery_dataset.pass_dataset",
        }

        failing_resources = {
            "google_bigquery_dataset.fail_special_group",
            "google_bigquery_dataset.fail_all_users",
            "google_bigquery_dataset.fail_new_key",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], len(failing_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()

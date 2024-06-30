import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.gcp.CloudArmorWAFACLCVE202144228 import check
from checkov.terraform.runner import Runner


class TestCloudArmorWAFACLCVE202144228(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_CloudArmorWAFACLCVE202144228"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "google_compute_security_policy.enabled_deny_403",
            "google_compute_security_policy.enabled_deny_404",
            "google_compute_security_policy.pass_preconfigwaf",
        }

        failing_resources = {
            "google_compute_security_policy.allow",
            "google_compute_security_policy.preview",
            "google_compute_security_policy.different_expr",
            "google_compute_security_policy.pass_preconfigwaf"
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], len(failing_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)

        # check especially for the evaluated keys
        actual_evaluated_keys = next(
            c.check_result["evaluated_keys"]
            for c in report.failed_checks
            if c.resource == "google_compute_security_policy.different_expr"
        )
        expected_evaluated_keys = [
            "rule/[0]/action",
            "rule/[0]/preview",
            "rule/[0]/match/[0]/expr/[0]/expression",
        ]
        self.assertCountEqual(expected_evaluated_keys, actual_evaluated_keys)


if __name__ == "__main__":
    unittest.main()

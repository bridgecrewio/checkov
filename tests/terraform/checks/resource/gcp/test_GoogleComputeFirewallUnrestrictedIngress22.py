import os
import unittest
from pathlib import Path

import mock

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.gcp.GoogleComputeFirewallUnrestrictedIngress22 import check
from checkov.terraform.runner import Runner


class TestGoogleComputeFirewallUnrestrictedIngress22(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_GoogleComputeFirewallUnrestrictedIngress22"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "google_compute_firewall.restricted",
            "google_compute_firewall.allow_null",
            "google_compute_firewall.allow_different_int",
            "google_compute_firewall.firewall_demo[\"firewall-02\"]",
            "google_compute_firewall.firewall_demo[\"firewall-04\"]",
            "google_compute_firewall.firewall_demo[\"firewall-05\"]",
            "google_compute_firewall.firewall_demo[\"firewall-06\"]",
        }

        failing_resources = {
            "google_compute_firewall.allow_multiple",
            "google_compute_firewall.allow_ssh_int",
            "google_compute_firewall.allow_all",
            "google_compute_firewall.firewall_demo[\"firewall-01\"]",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], len(passed_check_resources))
        self.assertEqual(summary["failed"], len(failed_check_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)
        self.assertEqual(summary["resource_count"], 12)  # 1 unknown

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()

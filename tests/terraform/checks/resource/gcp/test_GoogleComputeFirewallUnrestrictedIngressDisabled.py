import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.gcp.GoogleComputeFirewallUnrestrictedIngress22 import check as check_22
from checkov.terraform.checks.resource.gcp.GoogleComputeFirewallUnrestrictedIngress3389 import check as check_3389
from checkov.terraform.runner import Runner


class TestGoogleComputeFirewallUnrestrictedIngressDisabled(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_GoogleComputeFirewallUnrestrictedIngressDisabled"

        for check in (check_22, check_3389):
            with self.subTest(check=check.id):
                # when
                report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

                # then
                summary = report.get_summary()

                passing_resources = {
                    "google_compute_firewall.disabled_ssh_rdp",
                }

                failing_resources = {
                    "google_compute_firewall.disabled_false_ssh_rdp",
                    "google_compute_firewall.disabled_unresolved_ssh_rdp",
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

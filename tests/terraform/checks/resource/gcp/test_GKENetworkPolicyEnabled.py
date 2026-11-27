import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.gcp.GKENetworkPolicyEnabled import check
from checkov.terraform.runner import Runner


class TestGKENetworkPolicyEnabled(unittest.TestCase):
    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = os.path.join(current_dir, "example_GKENetworkPolicyEnabled")
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "google_container_cluster.network_policy_enabled",
            "google_container_cluster.advanced_datapath_without_network_policy",
            "google_container_cluster.advanced_datapath_with_network_policy_disabled",
            "google_container_cluster.autopilot",
        }
        failing_resources = {
            "google_container_cluster.network_policy_disabled",
            "google_container_cluster.network_policy_omitted",
            "google_container_cluster.autopilot_disabled",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], len(failing_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)
        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)

    def test_evaluated_keys(self):
        self.assertEqual(
            check.get_evaluated_keys(),
            [
                "enable_autopilot",
                "datapath_provider",
                "network_policy/[0]/enabled",
            ],
        )


if __name__ == "__main__":
    unittest.main()

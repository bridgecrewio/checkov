import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.gcp.GKEMetadataServerIsEnabled import check
from checkov.terraform.runner import Runner


class TestGKEMetadataServerIsEnabled(unittest.TestCase):
    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        test_files_dir = os.path.join(current_dir, "test_GKEMetadataServerIsEnabled")
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "google_container_cluster.autopilot",
            "google_container_cluster.current_metadata_mode",
            "google_container_cluster.legacy_metadata_mode",
            "google_container_node_pool.current_metadata_mode",
            "google_container_node_pool.legacy_metadata_mode",
        }
        failing_resources = {
            "google_container_cluster.autopilot_disabled",
            "google_container_cluster.gce_metadata_mode",
            "google_container_cluster.node_config_omitted",
            "google_container_cluster.workload_metadata_config_omitted",
            "google_container_node_pool.gce_metadata_mode",
            "google_container_node_pool.node_config_omitted",
            "google_container_node_pool.workload_metadata_config_omitted",
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
                "node_config/[0]/workload_metadata_config/[0]/mode",
                "node_config/[0]/workload_metadata_config/[0]/node_metadata",
            ],
        )


if __name__ == "__main__":
    unittest.main()

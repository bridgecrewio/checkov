import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.ElasticsearchNodeToNodeEncryption import check
from checkov.terraform.runner import Runner


class TestElasticsearchNodeToNodeEncryption(unittest.TestCase):
    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_ElasticsearchNodeToNodeEncryption"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "aws_elasticsearch_domain.without_cluster_config",
            "aws_elasticsearch_domain.without_instance_count",
            "aws_elasticsearch_domain.instance_count_not_bigger_than_1",
            "aws_elasticsearch_domain.node_to_node_encryption_enabled",
            "aws_elasticsearch_domain.old_hcl",
            "aws_opensearch_domain.without_cluster_config",
            "aws_opensearch_domain.without_instance_count",
            "aws_opensearch_domain.instance_count_not_bigger_than_1",
            "aws_opensearch_domain.node_to_node_encryption_enabled",
            "aws_opensearch_domain.old_hcl"
        }
        failing_resources = {
            "aws_elasticsearch_domain.node_to_node_encryption_disabled",
            "aws_elasticsearch_domain.node_to_node_encryption_doesnt_exist",
            "aws_opensearch_domain.node_to_node_encryption_disabled",
            "aws_opensearch_domain.node_to_node_encryption_doesnt_exist",
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary["passed"], 10)
        self.assertEqual(summary["failed"], 4)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()

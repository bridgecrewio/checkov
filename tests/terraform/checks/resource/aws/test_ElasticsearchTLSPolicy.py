import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.ElasticsearchTLSPolicy import check
from checkov.terraform.runner import Runner


class TestElasticsearchTLSPolicy(unittest.TestCase):
    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_ElasticsearchTLSPolicy"
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "aws_elasticsearch_domain.pass",
            "aws_elasticsearch_domain.pass2",
            "aws_opensearch_domain.pass",
            "aws_opensearch_domain.pass2"
        }
        failing_resources = {
            "aws_elasticsearch_domain.fail",
            "aws_elasticsearch_domain.notset",
            "aws_opensearch_domain.fail",
            "aws_opensearch_domain.notset"
        }

        passed_check_resources = set([c.resource for c in report.passed_checks])
        failed_check_resources = set([c.resource for c in report.failed_checks])

        self.assertEqual(summary["passed"], 4)
        self.assertEqual(summary["failed"], 4)
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)


if __name__ == "__main__":
    unittest.main()

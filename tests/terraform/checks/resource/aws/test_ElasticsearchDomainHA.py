import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.ElasticsearchDomainHA import check
from checkov.terraform.runner import Runner


class TestElasticsearchDomainHA(unittest.TestCase):
    def test(self):
        # given
        test_files_dir = Path(__file__).parent / "example_ElasticsearchDomainHA"

        # when
        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))

        # then
        summary = report.get_summary()

        passing_resources = {
            "aws_elasticsearch_domain.pass",
            "aws_opensearch_domain.pass",
        }

        failing_resources = {
            "aws_elasticsearch_domain.fail",
            "aws_elasticsearch_domain.fail2",
            "aws_opensearch_domain.fail",
            "aws_opensearch_domain.fail2",
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

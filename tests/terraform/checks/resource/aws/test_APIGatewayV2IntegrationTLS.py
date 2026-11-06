import os
import unittest

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.aws.APIGatewayV2IntegrationTLS import check
from checkov.terraform.runner import Runner


class TestAPIGatewayV2IntegrationTLS(unittest.TestCase):

    def test(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = os.path.join(current_dir, "example_APIGatewayV2IntegrationTLS")
        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "aws_apigatewayv2_integration.pass_vpc_link_tls",
            "aws_apigatewayv2_integration.pass_internet",
            "aws_apigatewayv2_integration.pass_no_connection_type",
        }
        failing_resources = {
            "aws_apigatewayv2_integration.fail_no_tls_config",
            "aws_apigatewayv2_integration.fail_empty_server_name",
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

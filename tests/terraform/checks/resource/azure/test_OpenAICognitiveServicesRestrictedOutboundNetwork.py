import unittest
from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.terraform.checks.resource.azure.OpenAICognitiveServicesRestrictOutboundNetwork import check
from checkov.terraform.runner import Runner


class TestOpenAICognitiveServicesRestrictedOutboundNetwork(unittest.TestCase):
    def test(self):
        test_files_dir = Path(__file__).parent / "example_OpenAICognitiveServicesRestrictOutboundNetwork"

        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "azurerm_cognitive_account.pass_openai",
            "azurerm_cognitive_account.pass_non_openai",
            "azurerm_cognitive_account.pass_openai_multiple_fqdns",
        }
        failing_resources = {
            "azurerm_cognitive_account.fail_openai_missing_fqdns",
            "azurerm_cognitive_account.fail_openai_missing_outbound_network_access",
            "azurerm_cognitive_account.fail_openai_missing_fqdns_and_outbound_network_access",
            "azurerm_cognitive_account.fail_openai_missing_fqdns_but_present_outbound_network_access",
            "azurerm_cognitive_account.fail_openai_no_outbound_access_and_multiple_fqdns",
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
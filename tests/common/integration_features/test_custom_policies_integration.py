import os
import unittest

from checkov.common.bridgecrew.integration_features.features.custom_policies_integration import \
    CustomPoliciesIntegration
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
from checkov.common.checks_infra.checks_parser import NXGraphCheckParser
from checkov.common.checks_infra.registry import Registry
from checkov.terraform.runner import Runner
from checkov.runner_filter import RunnerFilter
from pathlib import Path

class TestCustomPoliciesIntegration(unittest.TestCase):

    def test_integration_valid(self):
        instance = BcPlatformIntegration()
        instance.skip_policy_download = False
        instance.platform_integration_configured = True

        custom_policies_integration = CustomPoliciesIntegration(instance)

        self.assertTrue(custom_policies_integration.is_valid())

        instance.skip_policy_download = True
        self.assertFalse(custom_policies_integration.is_valid())

        instance.platform_integration_configured = False
        self.assertFalse(custom_policies_integration.is_valid())

        instance.skip_policy_download = False
        self.assertFalse(custom_policies_integration.is_valid())

    def test_policy_load(self):
        # response from API
        policies = [
            {
                "provider": "AWS",
                "id": "mikepolicies_AWS_1625063607541",
                "title": "yaml1",
                "severity": "MEDIUM",
                "category": "General",
                "resourceTypes": [
                    "aws_s3_bucket"
                ],
                "accountsData": {
                    "mikeurbanski1/terragoat3": {
                        "amounts": {
                            "CLOSED": 0,
                            "DELETED": 0,
                            "OPEN": 1,
                            "REMEDIATED": 0,
                            "SUPPRESSED": 0
                        },
                        "lastUpdateDate": "2021-06-30T14:33:54.638Z"
                    }
                },
                "guideline": "yaml1",
                "isCustom": True,
                "conditionQuery": {
                    "or": [
                        {
                            "value": "xyz",
                            "operator": "equals",
                            "attribute": "xyz",
                            "cond_type": "attribute",
                            "resource_types": [
                                "aws_s3_bucket"
                            ]
                        }
                    ]
                },
                "benchmarks": {},
                "createdBy": "mike+policies@bridgecrew.io",
                "code": "---\nmetadata:\n  name: \"yaml1\" #give your custom policy a unique name \n  guidelines: \"yaml1\" #add text that explains the configuration the policy looks for, its implications, and how to fix it\n  category: \"general\" #choose one: \"general\"/\"elaticsearch\"/\"iam\"/\"kubernetes\"/\"logging\"/\"monitoring\"/\"networking\"/\"public\"/\"secrets\"/\"serverless\"/\"storage\"\n  severity: \"medium\" #choose one: \"critical\"/\"high\"/\"medium\"/\"low\"/\"info\"\nscope:\n  provider: \"aws\" #choose one: \"aws\"/\"azure\"/\"gcp\"\ndefinition: #define the conditions the policy searches for.\n or:\n  - cond_type: \"attribute\"\n    resource_types:\n    - \"aws_s3_bucket\"\n    attribute: \"xyz\"\n    operator: \"equals\"\n    value: \"xyz\"\n#   - cond_type: \"attribute\"\n#     resource_types:\n#     - \"aws_instance\"\n#     attribute: \"instance_type\"\n#     operator: \"equals\"\n#     value: \"t3.nano\"\n"
            },
            {
                "provider": "AWS",
                "id": "mikepolicies_aws_1625063842021",
                "title": "ui1",
                "severity": "HIGH",
                "category": "General",
                "resourceTypes": [
                    "aws_s3_bucket"
                ],
                "accountsData": {
                    "mikeurbanski1/terragoat3": {
                        "amounts": {
                            "CLOSED": 0,
                            "DELETED": 0,
                            "OPEN": 1,
                            "REMEDIATED": 0,
                            "SUPPRESSED": 0
                        },
                        "lastUpdateDate": "2021-06-30T14:42:29.534Z"
                    }
                },
                "guideline": "ui1",
                "isCustom": True,
                "conditionQuery": {
                    "value": "abc",
                    "operator": "equals",
                    "attribute": "region",
                    "cond_type": "attribute",
                    "resource_types": [
                        "aws_s3_bucket"
                    ]
                },
                "benchmarks": {},
                "createdBy": "mike+policies@bridgecrew.io",
                "code": None
            }
        ]

        # for this test, we simulate some of the check registry manipulation; otherwise the singleton
        # instance will be modified and break other tests.

        parser = NXGraphCheckParser()

        registry = Registry(parser=NXGraphCheckParser(), checks_dir=str(
            Path(__file__).parent.parent.parent.parent / "checkov" / "terraform" / "checks" / "graph_checks"))
        checks = [parser.parse_raw_check(CustomPoliciesIntegration._convert_raw_check(p)) for p in policies]
        registry.checks = checks  # simulate that the policy downloader will do

        runner = Runner(external_registries=[registry])
        current_dir = os.path.dirname(os.path.realpath(__file__))

        test_files_dir = current_dir + "/example_custom_policy_dir"

        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter())
        self.assertEqual(len([r for r in report.failed_checks if r.check_id == 'mikepolicies_aws_1625063842021']), 1)
        self.assertEqual(len([r for r in report.failed_checks if r.check_id == 'mikepolicies_AWS_1625063607541']), 1)

        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(checks=['mikepolicies_aws_1625063842021']))
        self.assertEqual(len([r for r in report.failed_checks if r.check_id == 'mikepolicies_aws_1625063842021']), 1)
        self.assertEqual(len([r for r in report.failed_checks if r.check_id == 'mikepolicies_AWS_1625063607541']), 0)

        report = runner.run(root_folder=test_files_dir, runner_filter=RunnerFilter(skip_checks=['mikepolicies_aws_1625063842021']))
        self.assertEqual(len([r for r in report.failed_checks if r.check_id == 'mikepolicies_aws_1625063842021']), 0)
        self.assertEqual(len([r for r in report.failed_checks if r.check_id == 'mikepolicies_AWS_1625063607541']), 1)


if __name__ == '__main__':
    unittest.main()

import unittest
from pathlib import Path

from checkov.cloudformation.checks.resource.aws.LambdaEnvironmentCredentials import check
from checkov.cloudformation.runner import Runner
from checkov.common.models.enums import CheckResult
from checkov.runner_filter import RunnerFilter


class TestLambdaEnvironmentCredentials(unittest.TestCase):
    def test_summary(self):
        test_files_dir = Path(__file__).parent / "example_LambdaEnvironmentCredentials"

        report = Runner().run(root_folder=str(test_files_dir), runner_filter=RunnerFilter(checks=[check.id]))
        summary = report.get_summary()

        passing_resources = {
            "AWS::Lambda::Function.NoEnv",
            "AWS::Lambda::Function.NoSecret",
            "AWS::Lambda::Function.EnvNull",
            "AWS::Lambda::Function.UnresolvedEnv",
            "AWS::Serverless::Function.NoEnv",
            "AWS::Serverless::Function.NoProperties",
            "AWS::Serverless::Function.NoSecret",
            "AWS::Lambda::Function.Pass2",
            "AWS::Lambda::Function.CDKLambda",
        }
        failing_resources = {
            "AWS::Lambda::Function.Secret",
            "AWS::Serverless::Function.Secret",
        }

        passed_check_resources = {c.resource for c in report.passed_checks}
        failed_check_resources = {c.resource for c in report.failed_checks}

        self.assertEqual(summary["passed"], len(passing_resources))
        self.assertEqual(summary["failed"], len(failing_resources))
        self.assertEqual(summary["skipped"], 0)
        self.assertEqual(summary["parsing_errors"], 0)

        self.assertEqual(passing_resources, passed_check_resources)
        self.assertEqual(failing_resources, failed_check_resources)

    def test_parser_metadata_does_not_trigger_false_positive(self):
        # Issue #7310: parser injects __file__, __startline__, __endline__ into Variables mapping
        conf = {
            "Type": "AWS::Lambda::Function",
            "Properties": {
                "Environment": {
                    "Variables": {
                        "TABLE_NAME": {"Ref": "Table"},
                        "__file__": "/x-home/runner/work/devi/deviz/backend/devi-backend.yaml",
                        "__startline__": 10,
                        "__endline__": 20,
                    }
                }
            },
        }
        result = check.scan_resource_conf(conf)
        self.assertEqual(result, CheckResult.PASSED)
        self.assertEqual(check.evaluated_keys, ["Properties/Environment/Variables"])

    def test_double_underscore_user_variable_secret_detected(self):
        # Ensure user-defined environment variables with double underscores are still scanned
        conf = {
            "Type": "AWS::Lambda::Function",
            "Properties": {
                "Environment": {
                    "Variables": {
                        "__API_KEY__": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                        "__file__": "/normal/path/template.yaml",
                        "__startline__": 10,
                        "__endline__": 20,
                    }
                }
            },
        }
        result = check.scan_resource_conf(conf)
        self.assertEqual(result, CheckResult.FAILED)
        self.assertEqual(check.evaluated_keys, ["Properties/Environment/Variables/__API_KEY__"])

    def test_ordinary_environment_variables_pass(self):
        conf = {
            "Type": "AWS::Lambda::Function",
            "Properties": {
                "Environment": {
                    "Variables": {
                        "ENV": "production",
                        "REGION": "us-east-1",
                    }
                }
            },
        }
        result = check.scan_resource_conf(conf)
        self.assertEqual(result, CheckResult.PASSED)
        self.assertEqual(check.evaluated_keys, ["Properties/Environment/Variables"])

    def test_intrinsic_ref_values_supported(self):
        conf = {
            "Type": "AWS::Lambda::Function",
            "Properties": {
                "Environment": {
                    "Variables": {
                        "DB_HOST": {"Fn::GetAtt": ["DBCluster", "Endpoint.Address"]},
                        "TABLE": {"Ref": "DynamoTable"},
                    }
                }
            },
        }
        result = check.scan_resource_conf(conf)
        self.assertEqual(result, CheckResult.PASSED)
        self.assertEqual(check.evaluated_keys, ["Properties/Environment/Variables"])

    def test_variables_with_only_parser_metadata_pass(self):
        conf = {
            "Type": "AWS::Lambda::Function",
            "Properties": {
                "Environment": {
                    "Variables": {
                        "__file__": "/x-home/runner/work/devi/deviz/backend/devi-backend.yaml",
                        "__startline__": 1,
                        "__endline__": 2,
                    }
                }
            },
        }
        result = check.scan_resource_conf(conf)
        self.assertEqual(result, CheckResult.PASSED)
        self.assertEqual(check.evaluated_keys, ["Properties/Environment/Variables"])

    def test_empty_variables_dictionary_pass(self):
        conf = {
            "Type": "AWS::Lambda::Function",
            "Properties": {
                "Environment": {
                    "Variables": {}
                }
            },
        }
        result = check.scan_resource_conf(conf)
        self.assertEqual(result, CheckResult.PASSED)
        self.assertEqual(check.evaluated_keys, ["Properties/Environment/Variables"])


if __name__ == "__main__":
    unittest.main()

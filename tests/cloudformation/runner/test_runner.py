import dis
import inspect
import os
import unittest
from collections import defaultdict
from pathlib import Path
from typing import Dict, Any

import pytest
from parameterized import parameterized_class

from checkov.cloudformation.checks.resource.registry import cfn_registry
from checkov.cloudformation import cfn_utils
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.cloudformation.parser import parse
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.severities import BcSeverities, Severities
from checkov.common.graph.db_connectors.igraph.igraph_db_connector import IgraphConnector
from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.runner_filter import RunnerFilter
from checkov.cloudformation.runner import Runner
from checkov.common.output.report import Report
from checkov.cloudformation.cfn_utils import create_definitions

RESOURCES_DIR = Path(__file__).parent / "resources"


@parameterized_class([
   {"db_connector": NetworkxConnector},
   {"db_connector": IgraphConnector}
])
class TestRunnerValid(unittest.TestCase):

    def setUp(self) -> None:
        self.orig_checks = cfn_registry.checks

    def test_registry_has_type(self):
        self.assertEqual(cfn_registry.report_type, CheckType.CLOUDFORMATION)

    def test_record_relative_path_with_relative_dir(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "resources")

        # this is the relative path to the directory to scan (what would actually get passed to the -d arg)
        dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')

        runner = Runner(db_connector=self.db_connector())
        checks_allowlist = ['CKV_AWS_20']
        report = runner.run(root_folder=dir_rel_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='cloudformation', checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            # no need to join with a '/' because the CFN runner adds it to the start of the file path
            self.assertEqual(record.repo_file_path, f'/{dir_rel_path}{record.file_path}')

    def test_record_relative_path_with_abs_dir(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "resources")

        dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')

        dir_abs_path = os.path.abspath(scan_dir_path)

        runner = Runner(db_connector=self.db_connector())
        checks_allowlist = ['CKV_AWS_20']
        report = runner.run(root_folder=dir_abs_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='cloudformation', checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            # no need to join with a '/' because the CFN runner adds it to the start of the file path
            self.assertEqual(record.repo_file_path, f'/{dir_rel_path}{record.file_path}')

    def test_record_relative_path_with_relative_file(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "success.json")

        # this is the relative path to the file to scan (what would actually get passed to the -f arg)
        file_rel_path = os.path.relpath(scan_file_path)

        runner = Runner(db_connector=self.db_connector())
        checks_allowlist = ['CKV_AWS_20']
        report = runner.run(root_folder=None, external_checks_dir=None, files=[file_rel_path],
                            runner_filter=RunnerFilter(framework='cloudformation', checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            # no need to join with a '/' because the CFN runner adds it to the start of the file path
            self.assertEqual(record.repo_file_path, f'/{file_rel_path}')

    def test_record_relative_path_with_abs_file(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "success.json")

        file_rel_path = os.path.relpath(scan_file_path)
        file_abs_path = os.path.abspath(scan_file_path)

        runner = Runner(db_connector=self.db_connector())
        checks_allowlist = ['CKV_AWS_20']
        report = runner.run(root_folder=None, external_checks_dir=None, files=[file_abs_path],
                            runner_filter=RunnerFilter(framework='cloudformation', checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something
        for record in all_checks:
            # no need to join with a '/' because the CFN runner adds it to the start of the file path
            self.assertEqual(record.repo_file_path, f'/{file_rel_path}')

    def test_record_includes_custom_guideline(self):
        custom_guideline_url = "https://my.custom.url"
        custom_check_id = "MY_CUSTOM_CHECK"

        cfn_registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseResourceCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["AWS::SQS::Queue"],
                    guideline=custom_guideline_url
                )

            def scan_resource_conf(self, conf: Dict[str, Any], entity_type: str) -> CheckResult:
                return CheckResult.FAILED

        AnyFailingCheck()
        scan_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "fail.yaml")

        report = Runner(db_connector=self.db_connector()).run(
            None,
            files=[scan_file_path],
            runner_filter=RunnerFilter(framework='cloudformation', checks=[custom_check_id])
        )

        self.assertEqual(report.failed_checks[0].guideline, custom_guideline_url)

    def test_get_tags(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "tags.yaml")

        definitions, _ = parse(scan_file_path)

        resource_name = 'DataBucket'
        resource = definitions['Resources'][resource_name]
        entity = {resource_name: resource}
        entity_tags = cfn_utils.get_resource_tags(entity)

        self.assertEqual(len(entity_tags), 4)
        tags = {
            'Simple': 'Value',
            'Name': '${AWS::AccountId}-data',
            'Environment': 'long-form-sub-${account}',
            'Account': 'long-form-sub-${account}'
        }

        for name, value in tags.items():
            self.assertEqual(entity_tags[name], value)

        resource_name = 'NoTags'
        resource = definitions['Resources'][resource_name]
        entity = {resource_name: resource}
        entity_tags = cfn_utils.get_resource_tags(entity)

        self.assertIsNone(entity_tags)

        'TerraformServerAutoScalingGroup'
        resource_name = 'TerraformServerAutoScalingGroup'
        resource = definitions['Resources'][resource_name]
        entity = {resource_name: resource}
        entity_tags = cfn_utils.get_resource_tags(entity)

        self.assertDictEqual(
            entity_tags,
            {
                "Name": "TF-FulfillmentServer",
                "terraform-server-tag-key": "terraform-server-tag-value",
            }
        )

        resource_name = 'EKSClusterNodegroup'
        resource = definitions['Resources'][resource_name]
        entity = {resource_name: resource}
        entity_tags = cfn_utils.get_resource_tags(entity)

        self.assertDictEqual(
            entity_tags,
            {
                'Name': '{\'Ref\': \'ClusterName\'}-EKS-{\'Ref\': \'NodeGroupName\'}',
            }
        )

    def test_wrong_check_imports(self):
        wrong_imports = ["arm", "dockerfile", "helm", "kubernetes", "serverless", "terraform"]
        ignore_files = ["BaseCloudsplainingIAMCheck.py", "ECRPolicy.py"]
        check_imports = []

        checks_path = Path(inspect.getfile(Runner)).parent.joinpath("checks")
        for file in checks_path.rglob("*.py"):
            if file.name in ignore_files:
                continue

            with file.open() as f:
                instructions = dis.get_instructions(f.read())
                import_names = [instr.argval for instr in instructions if "IMPORT_NAME" == instr.opname]

                for import_name in import_names:
                    wrong_import = next((import_name for x in wrong_imports if x in import_name), None)
                    if wrong_import:
                        check_imports.append({file.name: wrong_import})

        assert len(check_imports) == 0, f"Wrong imports were added: {check_imports}"

    @pytest.mark.skip("No graph checks implemented yet for cloudformation")
    def test_run_graph_checks(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "../graph/checks/resources/MSKClusterLogging")


        dir_abs_path = os.path.abspath(scan_dir_path)

        report = Runner(db_connector=self.db_connector()).run(
            root_folder=dir_abs_path,
            external_checks_dir=None,
            runner_filter=RunnerFilter(framework=["cloudformation"], download_external_modules=False)
        )

        self.assertGreater(len(report.failed_checks), 0)
        self.assertGreater(len(report.passed_checks), 0)

    def test_external_data(self):
        dir_abs_path = os.path.dirname(os.path.realpath(__file__))

        definitions = {
            f'{dir_abs_path}/s3.yaml': {
                'Resources': {
                    'MySourceQueue': {
                        'Type': 'AWS::SQS::Queue',
                        'Properties': {
                            'KmsMasterKeyId': 'kms_id',
                            '__startline__': 17,
                            '__endline__': 22,
                            'resource_type': 'AWS::SQS::Queue'
                        }
                    },
                    'MyDB': {
                        'Type': 'AWS::RDS::DBInstance',
                        'Properties': {
                            'DBName': 'db',
                            'DBInstanceClass': 'db.t3.micro',
                            'Engine': 'mysql',
                            'MasterUsername': 'master',
                            'MasterUserPassword': 'password',  # checkov:skip=CKV_SECRET_6 test secret
                            '__startline__': 23,
                            '__endline__': 32,
                            'resource_type': 'AWS::RDS::DBInstance'
                        }
                    }
                }
            }
        }

        context = {
            f"{dir_abs_path}/s3.yaml": {
                "Parameters": {
                    "KmsMasterKeyId": {
                        "start_line": 5,
                        "end_line": 9,
                        "code_lines": [
                            (5, '    "KmsMasterKeyId": {\n'),
                            (6, '      "Description": "Company Name",\n'),
                            (7, '      "Type": "String",\n'),
                            (8, '      "Default": "kms_id"\n'),
                            (9, "    },\n"),
                        ],
                    },
                    "DBName": {
                        "start_line": 10,
                        "end_line": 14,
                        "code_lines": [
                            (10, '    "DBName": {\n'),
                            (11, '      "Description": "Name of the Database",\n'),
                            (12, '      "Type": "String",\n'),
                            (13, '      "Default": "db"\n'),
                            (14, "    }\n"),
                        ],
                    },
                },
                "Resources": {
                    "MySourceQueue": {
                        "start_line": 17,
                        "end_line": 22,
                        "code_lines": [
                            (17, '    "MySourceQueue": {\n'),
                            (18, '      "Type": "AWS::SQS::Queue",\n'),
                            (19, '      "Properties": {\n'),
                            (20, '        "KmsMasterKeyId": { "Ref": "KmsMasterKeyId" }\n'),
                            (21, "      }\n"),
                            (22, "    },\n"),
                        ],
                        "skipped_checks": [],
                    },
                    "MyDB": {
                        "start_line": 23,
                        "end_line": 32,
                        "code_lines": [
                            (23, '    "MyDB": {\n'),
                            (24, '      "Type": "AWS::RDS::DBInstance",\n'),
                            (25, '      "Properties": {\n'),
                            (26, '        "DBName": { "Ref": "DBName" },\n'),
                            (27, '        "DBInstanceClass": "db.t3.micro",\n'),
                            (28, '        "Engine": "mysql",\n'),
                            (29, '        "MasterUsername": "master",\n'),
                            (30, '        "MasterUserPassword": "password"\n'),
                            (31, "      }\n"),
                            (32, "    }\n"),
                        ],
                        "skipped_checks": [],
                    },
                },
                "Outputs": {
                    "DBAppPublicDNS": {
                        "start_line": 35,
                        "end_line": 38,
                        "code_lines": [
                            (35, '    "DBAppPublicDNS": {\n'),
                            (36, '      "Description": "DB App Public DNS Name",\n'),
                            (37, '      "Value": { "Fn::GetAtt" : [ "MyDB", "PublicDnsName" ] }\n'),
                            (38, "    }\n"),
                        ],
                    }
                },
            }
        }
        breadcrumbs = {}
        runner = Runner(db_connector=self.db_connector())
        runner.set_external_data(definitions, context, breadcrumbs)
        report = Report('cloudformation')
        runner.check_definitions(root_folder=dir_abs_path, runner_filter=RunnerFilter(framework='cloudformation', download_external_modules=False), report=report)
        self.assertEqual(len(report.passed_checks), 2)
        self.assertEqual(len(report.failed_checks), 4)
        pass

    def test_breadcrumbs_report(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "../graph/graph_builder/resources/variable_rendering/render_params")

        dir_abs_path = os.path.abspath(scan_dir_path)

        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=dir_abs_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='cloudformation', download_external_modules=False, checks=["CKV_AWS_21"]))

        self.assertEqual(1, len(report.failed_checks))
        self.assertIsNotNone(report.failed_checks[0].breadcrumbs)
        self.assertIsNotNone(report.failed_checks[0].breadcrumbs.get("VersioningConfiguration.Status"))

    def test_parsing_invalid_properties_yaml(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "invalid_properties.yaml")
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=None, external_checks_dir=None, files=[scan_file_path],
                            runner_filter=RunnerFilter(framework='cloudformation'))
        self.assertEqual(report.parsing_errors, [scan_file_path])

    def test_parsing_invalid_properties_json(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "invalid_properties.json")
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=None, external_checks_dir=None, files=[scan_file_path],
                            runner_filter=RunnerFilter(framework='cloudformation'))
        self.assertEqual(report.parsing_errors, [scan_file_path])

    def test_parsing_no_properties_yaml(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "no_properties.yaml")
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=None, external_checks_dir=None, files=[scan_file_path],
                            runner_filter=RunnerFilter(framework='cloudformation'))
        self.assertEqual(len(report.failed_checks), 3)
        self.assertEqual(len(report.passed_checks), 2)

    def test_runner_honors_enforcement_rules(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "graph.yaml")
        runner = Runner(db_connector=self.db_connector())
        filter = RunnerFilter(framework=['cloudformation'], use_enforcement_rules=True)
        # this is not quite a true test, because the checks don't have severities. However, this shows that the check registry
        # passes the report type properly to RunnerFilter.should_run_check, and we have tests for that method
        filter.enforcement_rule_configs = {CheckType.CLOUDFORMATION: Severities[BcSeverities.OFF]}
        report = runner.run(root_folder=None, external_checks_dir=None, files=[scan_file_path], runner_filter=filter)
        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.skipped_checks), 0)
        self.assertEqual(len(report.parsing_errors), 0)

    def test_parsing_no_properties_json(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "no_properties.json")
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=None, external_checks_dir=None, files=[scan_file_path],
                            runner_filter=RunnerFilter(framework='cloudformation'))
        self.assertEqual(len(report.failed_checks), 3)
        self.assertEqual(len(report.passed_checks), 2)

    def test_parsing_error_yaml(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "invalid.yaml")
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=None, external_checks_dir=None, files=[scan_file_path],
                            runner_filter=RunnerFilter(framework='cloudformation'))
        self.assertEqual(report.parsing_errors, [scan_file_path])

    def test_skip_sub_dict_json(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "skip_sub_dict.json")
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=None, external_checks_dir=None, files=[scan_file_path],
                            runner_filter=RunnerFilter(framework='cloudformation'))
        self.assertEqual(len(report.failed_checks), 0)

    def test_parsing_error_json(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "invalid.json")
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=None, external_checks_dir=None, files=[scan_file_path],
                            runner_filter=RunnerFilter(framework='cloudformation'))
        self.assertEqual(report.parsing_errors, [scan_file_path])

    def test_parse_relevant_files_only(self):
        definitions, _ = create_definitions(None, ['main.tf'])
        # just check that we skip the file and return normally
        self.assertNotIn('main.tf', definitions)

    def test_record_includes_severity(self):
        custom_check_id = "MY_CUSTOM_CHECK"

        cfn_registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseResourceCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["AWS::SQS::Queue"]
                )

            def scan_resource_conf(self, conf: Dict[str, Any], entity_type: str) -> CheckResult:
                return CheckResult.FAILED

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.LOW]
        scan_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "fail.yaml")

        report = Runner(db_connector=self.db_connector()).run(
            None,
            files=[scan_file_path],
            runner_filter=RunnerFilter(framework=['cloudformation'], checks=[custom_check_id])
        )

        self.assertEqual(report.failed_checks[0].severity, Severities[BcSeverities.LOW])

    def test_severity_check_filter_omit(self):
        custom_check_id = "MY_CUSTOM_CHECK"

        cfn_registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseResourceCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["AWS::SQS::Queue"]
                )

            def scan_resource_conf(self, conf: Dict[str, Any], entity_type: str) -> CheckResult:
                return CheckResult.FAILED

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.LOW]

        runner = Runner(db_connector=self.db_connector())
        checks_allowlist = ['MEDIUM']
        scan_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "fail.yaml")
        report = runner.run(None, files=[scan_file_path], external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='cloudformation', checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertFalse(any(c.check_id == custom_check_id for c in all_checks))

    def test_severity_check_filter_include(self):

        custom_check_id = "MY_CUSTOM_CHECK"

        cfn_registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseResourceCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["AWS::SQS::Queue"]
                )

            def scan_resource_conf(self, conf: Dict[str, Any], entity_type: str) -> CheckResult:
                return CheckResult.FAILED

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.HIGH]

        runner = Runner(db_connector=self.db_connector())
        checks_allowlist = ['MEDIUM']
        scan_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "fail.yaml")
        report = runner.run(None, files=[scan_file_path], external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='cloudformation', checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertTrue(any(c.check_id == custom_check_id for c in all_checks))

    def test_severity_skip_check_filter_omit(self):

        custom_check_id = "MY_CUSTOM_CHECK"

        cfn_registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseResourceCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["AWS::SQS::Queue"]
                )

            def scan_resource_conf(self, conf: Dict[str, Any], entity_type: str) -> CheckResult:
                return CheckResult.FAILED

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.LOW]

        runner = Runner(db_connector=self.db_connector())
        checks_denylist = ['MEDIUM']
        scan_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "fail.yaml")
        report = runner.run(None, files=[scan_file_path], external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='cloudformation', skip_checks=checks_denylist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertFalse(any(c.check_id == custom_check_id for c in all_checks))

    def test_severity_skip_check_filter_include(self):

        custom_check_id = "MY_CUSTOM_CHECK"

        cfn_registry.checks = defaultdict(list)

        class AnyFailingCheck(BaseResourceCheck):
            def __init__(self, *_, **__) -> None:
                super().__init__(
                    "this should fail",
                    custom_check_id,
                    [CheckCategories.ENCRYPTION],
                    ["AWS::SQS::Queue"]
                )

            def scan_resource_conf(self, conf: Dict[str, Any], entity_type: str) -> CheckResult:
                return CheckResult.FAILED

        check = AnyFailingCheck()
        check.severity = Severities[BcSeverities.HIGH]

        runner = Runner(db_connector=self.db_connector())
        checks_denylist = ['MEDIUM']
        scan_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "fail.yaml")
        report = runner.run(None, files=[scan_file_path], external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='cloudformation', skip_checks=checks_denylist))

        all_checks = report.failed_checks + report.passed_checks
        self.assertTrue(any(c.check_id == custom_check_id for c in all_checks))

    def test_graph_check_suppressions(self):
        # given
        test_file = RESOURCES_DIR / "suppress_graph_check.yaml"

        # when
        report = Runner(db_connector=self.db_connector()).run(
            root_folder=None,
            files=[str(test_file)],
            runner_filter=RunnerFilter(framework=["cloudformation"], checks=["CKV2_AWS_33"]),
        )

        # then
        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(len(report.passed_checks), 0)
        self.assertEqual(len(report.skipped_checks), 2)

    def tearDown(self):
        cfn_registry.checks = self.orig_checks


if __name__ == '__main__':
    unittest.main()

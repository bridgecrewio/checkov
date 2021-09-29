import inspect
import json
import os
import unittest
import dis
from pathlib import Path

from checkov.common.checks_infra.registry import get_graph_checks_registry
from checkov.common.models.consts import SCAN_HCL_FLAG
from checkov.common.output.report import Report
from checkov.runner_filter import RunnerFilter
from checkov.terraform.context_parsers.registry import parser_registry
from checkov.terraform.parser import Parser
from checkov.terraform.runner import Runner, resource_registry

CUSTOM_GRAPH_CHECK_ID = 'CKV2_CUSTOM_1'


class TestRunnerValid(unittest.TestCase):

    def test_runner_two_checks_only(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/example"
        runner = Runner()
        checks_allowlist = ['CKV_AWS_41', 'CKV_AZURE_1']
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='all', checks=checks_allowlist))
        report_json = report.get_json()
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suites())
        for record in report.failed_checks:
            self.assertIn(record.check_id, checks_allowlist)

    def test_runner_denylist_checks(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/example"
        runner = Runner()
        checks_denylist = ['CKV_AWS_41', 'CKV_AZURE_1']
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='all', skip_checks=checks_denylist))
        report_json = report.get_json()
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suites())
        self.assertEqual(report.get_exit_code(soft_fail=False), 1)
        self.assertEqual(report.get_exit_code(soft_fail=True), 0)
        for record in report.failed_checks:
            self.assertNotIn(record.check_id, checks_denylist)

    def test_runner_valid_tf(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/example"
        runner = Runner()
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None)
        report_json = report.get_json()
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suites())
        self.assertEqual(report.get_exit_code(soft_fail=False), 1)
        self.assertEqual(report.get_exit_code(soft_fail=True), 0)
        summary = report.get_summary()
        self.assertGreaterEqual(summary['passed'], 1)
        self.assertGreaterEqual(summary['failed'], 1)
        self.assertEqual(summary["parsing_errors"], 1)
        report.print_json()
        report.print_console()
        report.print_console(is_quiet=True)
        report.print_console(is_quiet=True, is_compact=True)
        report.print_junit_xml()
        report.print_failed_github_md()

    def test_runner_passing_valid_tf(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        passing_tf_dir_path = current_dir + "/resources/valid_tf_only_passed_checks"

        print("testing dir" + passing_tf_dir_path)
        runner = Runner()
        report = runner.run(root_folder=passing_tf_dir_path, external_checks_dir=None)
        report_json = report.get_json()
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suites())
        self.assertEqual(report.get_exit_code(False), 1)
        summary = report.get_summary()
        self.assertGreaterEqual(summary['passed'], 1)
        self.assertEqual(3, summary['failed'])
        self.assertEqual(1, summary['skipped'])
        self.assertEqual(0, summary["parsing_errors"])

    def test_runner_passing_multi_line_ternary_tf(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        tf_dir_path = current_dir + "/resources/mutli_line_ternary"

        print("testing dir" + tf_dir_path)
        runner = Runner()
        report = runner.run(root_folder=tf_dir_path, external_checks_dir=None)
        self.assertListEqual(report.parsing_errors, [])

    def test_runner_extra_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        tf_dir_path = current_dir + "/resources/extra_check_test"
        extra_checks_dir_path = [current_dir + "/extra_checks"]

        print("testing dir" + tf_dir_path)
        runner = Runner()
        report = runner.run(root_folder=tf_dir_path, external_checks_dir=extra_checks_dir_path)
        report_json = report.get_json()
        for check in resource_registry.checks["aws_s3_bucket"]:
            if check.id == "CUSTOM_AWS_1":
                resource_registry.checks["aws_s3_bucket"].remove(check)
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suites())

        passing_custom = 0
        failed_custom = 0
        for record in report.passed_checks:
            if record.check_id == "CUSTOM_AWS_1":
                passing_custom = passing_custom + 1
        for record in report.failed_checks:
            if record.check_id == "CUSTOM_AWS_1":
                failed_custom = failed_custom + 1

        self.assertEqual(1, passing_custom)
        self.assertEqual(2, failed_custom)
        # Remove external checks from registry.
        runner.graph_registry.checks[:] = [check for check in runner.graph_registry.checks if "CUSTOM" not in check.id]

    def test_runner_extra_yaml_check(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        tf_dir_path = current_dir + "/resources/extra_check_test"
        extra_checks_dir_path = [current_dir + "/extra_yaml_checks"]

        runner = Runner()
        report = runner.run(root_folder=tf_dir_path, external_checks_dir=extra_checks_dir_path)
        report_json = report.get_json()
        for check in resource_registry.checks["aws_s3_bucket"]:
            if check.id == "CKV2_CUSTOM_1":
                resource_registry.checks["aws_s3_bucket"].remove(check)
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suites())

        passing_custom = 0
        failed_custom = 0
        for record in report.passed_checks:
            if record.check_id == "CKV2_CUSTOM_1":
                passing_custom = passing_custom + 1
        for record in report.failed_checks:
            if record.check_id == "CKV2_CUSTOM_1":
                failed_custom = failed_custom + 1

        self.assertEqual(passing_custom, 0)
        self.assertEqual(failed_custom, 3)
        # Remove external checks from registry.
        runner.graph_registry.checks[:] = [check for check in runner.graph_registry.checks if "CUSTOM" not in check.id]

    def test_runner_specific_file(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        passing_tf_file_path = current_dir + "/resources/valid_tf_only_passed_checks/example.tf"

        runner = Runner()
        report = runner.run(root_folder=None, external_checks_dir=None, files=[passing_tf_file_path])
        report_json = report.get_json()
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suites())
        # self.assertEqual(report.get_exit_code(), 0)
        summary = report.get_summary()
        self.assertGreaterEqual(summary['passed'], 1)
        self.assertEqual(2, summary['failed'])
        self.assertEqual(0, summary["parsing_errors"])

    def test_check_ids_dont_collide(self):
        runner = Runner()
        unique_checks = {}
        bad_checks = []
        for registry in list(runner.block_type_registries.values()):
            checks = [check for entity_type in list(registry.checks.values()) for check in entity_type]
            for check in checks:
                if check.id not in unique_checks:
                    unique_checks[check.id] = check
                elif check != unique_checks[check.id]:
                    # A single check can have multiple resource blocks it checks, which means it will show up multiple times in the registry
                    bad_checks.append(f'{check.id}: {check.name}')
                    print(f'{check.id}: {check.name}')
        self.assertEqual(len(bad_checks), 0, f'Bad checks: {bad_checks}')

    def test_no_missing_ids(self):
        runner = Runner()
        unique_checks = set()
        for registry in list(runner.block_type_registries.values()):
            checks = [check for entity_type in list(registry.checks.values()) for check in entity_type]
            for check in checks:
                unique_checks.add(check.id)
        aws_checks = sorted(list(filter(lambda check_id: '_AWS_' in check_id, unique_checks)), reverse=True, key=lambda s: int(s.split('_')[-1]))
        for i in range(1, len(aws_checks) + 4):
            if f'CKV_AWS_{i}' == 'CKV_AWS_4':
                # CKV_AWS_4 was deleted due to https://github.com/bridgecrewio/checkov/issues/371
                continue
            if f'CKV_AWS_{i}' in ('CKV_AWS_132', 'CKV_AWS_125', 'CKV_AWS_151'):
                # These checks were removed because they were duplicates
                continue
            if f'CKV_AWS_{i}' in 'CKV_AWS_95':
                # CKV_AWS_95 is currently implemented just on cfn
                continue
            if f'CKV_AWS_{i}' == 'CKV_AWS_52':
                # CKV_AWS_52 was deleted since it cannot be toggled in terraform.
                continue
            self.assertIn(f'CKV_AWS_{i}', aws_checks, msg=f'The new AWS violation should have the ID "CKV_AWS_{i}"')

        gcp_checks = sorted(list(filter(lambda check_id: '_GCP_' in check_id, unique_checks)), reverse=True, key=lambda s: int(s.split('_')[-1]))
        for i in range(1, len(gcp_checks) + 1):
            if f'CKV_GCP_{i}' == 'CKV_GCP_5':
                # CKV_GCP_5 is no longer a valid platform check
                continue

            self.assertIn(f'CKV_GCP_{i}', gcp_checks, msg=f'The new GCP violation should have the ID "CKV_GCP_{i}"')

        azure_checks = sorted(list(filter(lambda check_id: '_AZURE_' in check_id, unique_checks)), reverse=True, key=lambda s: int(s.split('_')[-1]))
        for i in range(1, len(azure_checks) + 1):
            if f'CKV_AZURE_{i}' == 'CKV_AZURE_43':
                continue  # Pending merge; blocked by another issue https://github.com/bridgecrewio/checkov/pull/429
            if f'CKV_AZURE_{i}' == 'CKV_AZURE_51':
                continue  # https://github.com/bridgecrewio/checkov/pull/983

            self.assertIn(f'CKV_AZURE_{i}', azure_checks,
                          msg=f'The new Azure violation should have the ID "CKV_AZURE_{i}"')

        graph_registry = get_graph_checks_registry("terraform")
        graph_registry.load_checks()
        graph_checks = list(filter(lambda check: 'CKV2_' in check.id, graph_registry.checks))

        # add cloudformation checks to graph checks
        graph_registry = get_graph_checks_registry("cloudformation")
        graph_registry.load_checks()
        graph_checks.extend(list(filter(lambda check: 'CKV2_' in check.id, graph_registry.checks)))

        aws_checks, gcp_checks, azure_checks = [], [], []
        for check in graph_checks:
            if '_AWS_' in check.id:
                aws_checks.append(check.id)
            elif '_GCP_' in check.id:
                gcp_checks.append(check.id)
            elif '_AZURE_' in check.id:
                azure_checks.append(check.id)

        for check_list in [aws_checks, gcp_checks, azure_checks]:
            check_list.sort(reverse=True, key=lambda s: int(s.split('_')[-1]))

        for i in range(1, len(aws_checks) + 1):
            if f'CKV2_AWS_{i}' == 'CKV2_AWS_17':
                # CKV2_AWS_17 was overly keen and those resources it checks are created by default
                continue
            self.assertIn(f'CKV2_AWS_{i}', aws_checks,
                          msg=f'The new AWS violation should have the ID "CKV2_AWS_{i}"')
        for i in range(1, len(gcp_checks) + 1):
            self.assertIn(f'CKV2_GCP_{i}', gcp_checks,
                          msg=f'The new GCP violation should have the ID "CKV2_GCP_{i}"')
        for i in range(1, len(azure_checks) + 1):
            self.assertIn(f'CKV2_AZURE_{i}', azure_checks,
                          msg=f'The new Azure violation should have the ID "CKV2_AZURE_{i}"')

    def test_provider_uniqueness(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/many_providers"
        runner = Runner()
        result = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(checks='CKV_AWS_41'))
        self.assertEqual(len(result.passed_checks), 16)
        self.assertIn('aws.default', map(lambda record: record.resource, result.passed_checks))

    def test_terraform_module_checks_are_performed(self):
        check_name = "TF_M_1"

        from checkov.common.models.enums import CheckResult
        from checkov.terraform.checks.module.base_module_check import BaseModuleCheck
        from checkov.terraform.checks.module.registry import module_registry

        class ModuleCheck(BaseModuleCheck):

            def __init__(self):
                name = "Test check"
                id = check_name
                supported_resources = ['module']
                categories = []
                super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

            def scan_module_conf(self, conf):
                return CheckResult.PASSED

        check = ModuleCheck()

        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources/valid_tf_only_module_usage")
        runner = Runner()
        result = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(checks=check_name))

        # unregister check
        for resource in check.supported_resources:
            module_registry.checks[resource].remove(check)

        self.assertEqual(len(result.passed_checks), 1)
        self.assertIn('module.some-module', map(lambda record: record.resource, result.passed_checks))

    def test_terraform_module_checks_are_performed_even_if_supported_resources_is_omitted(self):
        check_name = "TF_M_2"

        from checkov.common.models.enums import CheckResult
        from checkov.terraform.checks.module.base_module_check import BaseModuleCheck
        from checkov.terraform.checks.module.registry import module_registry

        class ModuleCheck(BaseModuleCheck):

            def __init__(self):
                name = "Test check"
                id = check_name
                categories = []
                super().__init__(name=name, id=id, categories=categories)

            def scan_module_conf(self, conf):
                return CheckResult.PASSED

        check = ModuleCheck()

        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "resources/valid_tf_only_module_usage")
        runner = Runner()
        result = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(checks=check_name))

        # unregister check
        for resource in check.supported_resources:
            module_registry.checks[resource].remove(check)

        self.assertEqual(len(result.passed_checks), 1)
        self.assertIn('module.some-module', map(lambda record: record.resource, result.passed_checks))

    def test_parser_error_handled_for_directory_target(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        invalid_dir_path = os.path.join(current_dir, "resources/invalid_terraform_syntax")
        file_names = ['bad_tf_1.tf', 'bad_tf_2.tf']
        invalid_dir_abs_path = os.path.abspath(invalid_dir_path)

        runner = Runner()
        result = runner.run(root_folder=invalid_dir_path, external_checks_dir=None)

        self.assertEqual(len(result.parsing_errors), 2)
        for file in file_names:
            self.assertIn(os.path.join(invalid_dir_abs_path, file), result.parsing_errors)

    def test_parser_error_handled_for_file_target(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        invalid_dir_path = os.path.join(current_dir, "resources/invalid_terraform_syntax")
        file_names = ['bad_tf_1.tf', 'bad_tf_2.tf']
        invalid_dir_abs_path = os.path.abspath(invalid_dir_path)

        runner = Runner()
        result = runner.run(files=[os.path.join(invalid_dir_path, file) for file in file_names], root_folder=None,
                            external_checks_dir=None)

        self.assertEqual(len(result.parsing_errors), 2)
        for file in file_names:
            self.assertIn(os.path.join(invalid_dir_abs_path, file), result.parsing_errors)

    def test_typed_terraform_resource_checks_are_performed(self):
        test_self = self
        check_name = "TF_M_2"
        test_dir = "resources/valid_tf_only_resource_usage"

        from checkov.common.models.enums import CheckResult
        from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
        from checkov.terraform.checks.resource.registry import resource_registry

        class ResourceCheck(BaseResourceCheck):

            def __init__(self):
                name = "Test check"
                id = check_name
                supported_resources = ['*']
                categories = []
                super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

            def scan_entity_conf(self, conf, entity_type):
                if entity_type == 'type_1':
                    test_self.assertIn('a', conf)
                    test_self.assertEqual([1], conf['a'])
                elif entity_type == 'type_2':
                    test_self.assertIn('b', conf)
                    test_self.assertEqual([2], conf['b'])
                else:
                    test_self.fail(f'Unexpected entity_type: {entity_type}. Expected type_1 or type_2, because no '
                                   f'other resources are defined in the files inside of {test_dir}.')
                return CheckResult.PASSED

            def scan_resource_conf(self, conf):
                pass

        check = ResourceCheck()

        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, test_dir)
        runner = Runner()
        result = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(checks=check_name))

        # unregister check
        for resource in check.supported_resources:
            resource_registry.wildcard_checks[resource].remove(check)

        self.assertEqual(len(result.passed_checks), 2)

    def test_external_definitions_context(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        tf_dir_path = current_dir + "/resources/valid_tf_only_passed_checks"
        external_definitions_context = {
            f'{current_dir}/resources/valid_tf_only_passed_checks/example.tf': {
                'resource': {'aws_s3_bucket': {'foo-bucket': {'start_line': 1, 'end_line': 34, 'code_lines': [
                    (1, 'resource "aws_s3_bucket" "foo-bucket" {\n'), (2, '  region        = var.region\n'),
                    (3, '  bucket        = local.bucket_name\n'), (4, '  force_destroy = true\n'), (5, '  tags = {\n'),
                    (6, '    Name = "foo-${data.aws_caller_identity.current.account_id}"\n'), (7, '  }\n'),
                    (8, '  versioning {\n'), (9, '    enabled = true\n'), (10, '    mfa_delete = true\n'),
                    (11, '  }\n'), (12, '  logging {\n'),
                    (13, '    target_bucket = "${aws_s3_bucket.log_bucket.id}"\n'),
                    (14, '    target_prefix = "log/"\n'), (15, '  }\n'),
                    (16, '  server_side_encryption_configuration {\n'), (17, '    rule {\n'),
                    (18, '      apply_server_side_encryption_by_default {\n'),
                    (19, '        kms_master_key_id = "${aws_kms_key.mykey.arn}"\n'),
                    (20, '        sse_algorithm     = "aws:kms"\n'), (21, '      }\n'), (22, '    }\n'), (23, '  }\n'),
                    (24, '  acl           = "private"\n'), (25, '  tags = "${merge\n'), (26, '    (\n'),
                    (27, '      var.common_tags,\n'), (28, '      map(\n'),
                    (29, '        "name", "VM Virtual Machine",\n'), (30, '        "group", "foo"\n'),
                    (31, '      )\n'), (32, '    )\n'), (33, '  }"\n'), (34, '}\n')], 'skipped_checks': []}},
                             'null_resource': {'example': {'start_line': 36, 'end_line': 46, 'code_lines': [
                                 (36, 'resource "null_resource" "example" {\n'), (37, '  tags = "${merge\n'),
                                 (38, '(\n'), (39, 'var.common_tags,\n'), (40, 'map(\n'),
                                 (41, '"name", "VM Base Post Provisioning Library",\n'), (42, '"group", "aut",\n'),
                                 (43, '"dependency", "${var.input_dependency_value}")\n'), (44, ')\n'), (45, '}"\n'),
                                 (46, '}\n')], 'skipped_checks': []}}}, 'data': {'aws_caller_identity': {
                    'current': {'start_line': 47, 'end_line': 0, 'code_lines': [], 'skipped_checks': []}}},
                'provider': {'kubernetes': {'default': {'start_line': 49, 'end_line': 55,
                                                        'code_lines': [(49, 'provider "kubernetes" {\n'),
                                                                       (50, '  version                = "1.10.0"\n'), (
                                                                           51,
                                                                           '  host                   = module.aks_cluster.kube_config.0.host\n'),
                                                                       (52,
                                                                        '  client_certificate     = base64decode(module.aks_cluster.kube_config.0.client_certificate)\n'),
                                                                       (53,
                                                                        'client_key             = base64decode(module.aks_cluster.kube_config.0.client_key)\n'),
                                                                       (54,
                                                                        'cluster_ca_certificate = base64decode(module.aks_cluster.kube_config.0.cluster_ca_certificate)\n'),
                                                                       (55, '}\n')], 'skipped_checks': []}}},
                'module': {'module': {'new_relic': {'start_line': 57, 'end_line': 67,
                                                    'code_lines': [(57, 'module "new_relic" {\n'), (58,
                                                                                                    'source                            = "s3::https://s3.amazonaws.com/my-artifacts/new-relic-k8s-0.2.5.zip"\n'),
                                                                   (59,
                                                                    'kubernetes_host                   = module.aks_cluster.kube_config.0.host\n'),
                                                                   (60,
                                                                    'kubernetes_client_certificate     = base64decode(module.aks_cluster.kube_config.0.client_certificate)\n'),
                                                                   (61,
                                                                    'kubernetes_client_key             = base64decode(module.aks_cluster.kube_config.0.client_key)\n'),
                                                                   (62,
                                                                    'kubernetes_cluster_ca_certificate = base64decode(module.aks_cluster.kube_config.0.cluster_ca_certificate)\n'),
                                                                   (63,
                                                                    'cluster_name                      = module.naming_conventions.aks_name\n'),
                                                                   (64,
                                                                    'new_relic_license                 = data.vault_generic_secret.new_relic_license.data["license"]\n'),
                                                                   (65,
                                                                    'cluster_ca_bundle_b64             = module.aks_cluster.kube_config.0.cluster_ca_certificate\n'),
                                                                   (66,
                                                                    'module_depends_on                 = [null_resource.delay_aks_deployments]\n'),
                                                                   (67, '}')], 'skipped_checks': []}}}},
            f'{current_dir}/resources/valid_tf_only_passed_checks/example_skip_acl.tf': {
                'resource': {'aws_s3_bucket': {'foo-bucket': {'start_line': 1, 'end_line': 26, 'code_lines': [
                    (1, 'resource "aws_s3_bucket" "foo-bucket" {\n'), (2, '  region        = var.region\n'),
                    (3, '  bucket        = local.bucket_name\n'), (4, '  force_destroy = true\n'),
                    (5, '  #checkov:skip=CKV_AWS_20:The bucket is a public static content host\n'),
                    (6, '  #bridgecrew:skip=CKV_AWS_52: foo\n'), (7, '  tags = {\n'),
                    (8, '    Name = "foo-${data.aws_caller_identity.current.account_id}"\n'), (9, '  }\n'),
                    (10, '  versioning {\n'), (11, '    enabled = true\n'), (12, '  }\n'), (13, '  logging {\n'),
                    (14, '    target_bucket = "${aws_s3_bucket.log_bucket.id}"\n'),
                    (15, '    target_prefix = "log/"\n'), (16, '  }\n'),
                    (17, '  server_side_encryption_configuration {\n'), (18, '    rule {\n'),
                    (19, '      apply_server_side_encryption_by_default {\n'),
                    (20, '        kms_master_key_id = "${aws_kms_key.mykey.arn}"\n'),
                    (21, '        sse_algorithm     = "aws:kms"\n'), (22, '      }\n'), (23, '    }\n'), (24, '  }\n'),
                    (25, '  acl           = "public-read"\n'), (26, '}\n')], 'skipped_checks': [
                    {'id': 'CKV_AWS_20', 'suppress_comment': 'The bucket is a public static content host'},
                    {'id': 'CKV_AWS_52', 'suppress_comment': ' foo'}]}}}, 'data': {'aws_caller_identity': {
                    'current': {'start_line': 27, 'end_line': 0, 'code_lines': [], 'skipped_checks': []}}}}}
        tf_definitions = {'/mock/os/checkov_v2/tests/terraform/runner/resources/valid_tf_only_passed_checks/example.tf': {'resource': [{'aws_s3_bucket': {'foo-bucket': {'region': ['${var.region}'], 'bucket': ['${local.bucket_name}'], 'force_destroy': [True], 'versioning': [{'enabled': [True], 'mfa_delete': [True]}], 'logging': [{'target_bucket': ['${aws_s3_bucket.log_bucket.id}'], 'target_prefix': ['log/']}], 'server_side_encryption_configuration': [{'rule': [{'apply_server_side_encryption_by_default': [{'kms_master_key_id': ['${aws_kms_key.mykey.arn}'], 'sse_algorithm': ['aws:kms']}]}]}], 'acl': ['private'], 'tags': ['${merge\n    (\n      var.common_tags,\n      map(\n        "name", "VM Virtual Machine",\n        "group", "foo"\n      )\n    )\n  }']}}}], 'data': [{'aws_caller_identity': {'current': {}}}], 'provider': [{'kubernetes': {'version': ['1.10.0'], 'host': ['${module.aks_cluster.kube_config[0].host}'], 'client_certificate': ['${base64decode(module.aks_cluster.kube_config[0].client_certificate)}'], 'client_key': ['${base64decode(module.aks_cluster.kube_config[0].client_key)}'], 'cluster_ca_certificate': ['${base64decode(module.aks_cluster.kube_config[0].cluster_ca_certificate)}']}}], 'module': [{'new_relic': {'source': ['s3::https://s3.amazonaws.com/my-artifacts/new-relic-k8s-0.2.5.zip'], 'kubernetes_host': ['${module.aks_cluster.kube_config[0].host}'], 'kubernetes_client_certificate': ['${base64decode(module.aks_cluster.kube_config[0].client_certificate)}'], 'kubernetes_client_key': ['${base64decode(module.aks_cluster.kube_config[0].client_key)}'], 'kubernetes_cluster_ca_certificate': ['${base64decode(module.aks_cluster.kube_config[0].cluster_ca_certificate)}'], 'cluster_name': ['${module.naming_conventions.aks_name}'], 'new_relic_license': ['${data.vault_generic_secret.new_relic_license.data["license"]}'], 'cluster_ca_bundle_b64': ['${module.aks_cluster.kube_config[0].cluster_ca_certificate}'], 'module_depends_on': [['${null_resource.delay_aks_deployments}']]}}]}, '/mock/os/checkov_v2/tests/terraform/runner/resources/valid_tf_only_passed_checks/example_skip_acl.tf': {'resource': [{'aws_s3_bucket': {'foo-bucket': {'region': ['${var.region}'], 'bucket': ['${local.bucket_name}'], 'force_destroy': [True], 'tags': [{'Name': 'foo-${data.aws_caller_identity.current.account_id}'}], 'versioning': [{'enabled': [True]}], 'logging': [{'target_bucket': ['${aws_s3_bucket.log_bucket.id}'], 'target_prefix': ['log/']}], 'server_side_encryption_configuration': [{'rule': [{'apply_server_side_encryption_by_default': [{'kms_master_key_id': ['${aws_kms_key.mykey.arn}'], 'sse_algorithm': ['aws:kms']}]}]}], 'acl': ['public-read']}}}], 'data': [{'aws_caller_identity': {'current': {}}}]}}
        runner = Runner()
        parser = Parser()
        runner.definitions = tf_definitions
        runner.set_external_data(tf_definitions, external_definitions_context, breadcrumbs={})
        parser.parse_directory(tf_dir_path, tf_definitions)
        report = Report('terraform')
        runner.check_tf_definition(root_folder=tf_dir_path, report=report, runner_filter=RunnerFilter())
        self.assertGreaterEqual(len(report.passed_checks), 1)

    def test_failure_in_resolved_module(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = os.path.join(current_dir, "../parser/resources/parser_scenarios/module_matryoshka")
        valid_dir_path = os.path.normpath(valid_dir_path)
        runner = Runner()
        checks_allowlist = ['CKV_AWS_20']
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='terraform', checks=checks_allowlist))
        report_json = report.get_json()
        self.assertIsInstance(report_json, str)
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suites())
        self.assertEqual(report.get_exit_code(soft_fail=False), 1)
        self.assertEqual(report.get_exit_code(soft_fail=True), 0)

        self.assertEqual(checks_allowlist[0], report.failed_checks[0].check_id)
        self.assertEqual("/bucket1/bucket2/bucket3/bucket.tf", report.failed_checks[0].file_path)
        self.assertEqual(1, len(report.failed_checks))

        for record in report.failed_checks:
            self.assertIn(record.check_id, checks_allowlist)

    def test_record_relative_path_with_relative_dir(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_dir_path = os.path.join(current_dir, "resources", "nested_dir")

        # this is the relative path to the directory to scan (what would actually get passed to the -d arg)
        dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')

        runner = Runner()
        checks_allowlist = ['CKV_AWS_20']
        report = runner.run(root_folder=dir_rel_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='terraform', checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks

        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something

        for record in all_checks:
            # no need to join with a '/' because the TF runner adds it to the start of the file path
            self.assertEqual(record.repo_file_path, f'/{dir_rel_path}{record.file_path}')

    def test_record_relative_path_with_abs_dir(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))

        scan_dir_path = os.path.join(current_dir, "resources", "nested_dir")
        dir_rel_path = os.path.relpath(scan_dir_path).replace('\\', '/')
        dir_abs_path = os.path.abspath(scan_dir_path)

        runner = Runner()
        checks_allowlist = ['CKV_AWS_20']
        report = runner.run(root_folder=dir_abs_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='terraform', checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks

        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something

        for record in all_checks:
            # no need to join with a '/' because the TF runner adds it to the start of the file path
            self.assertEqual(record.repo_file_path, f'/{dir_rel_path}{record.file_path}')

    def test_record_relative_path_with_relative_file(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "nested_dir", "nested", "example.tf")

        # this is the relative path to the file to scan (what would actually get passed to the -f arg)
        file_rel_path = os.path.relpath(scan_file_path)

        runner = Runner()
        checks_allowlist = ['CKV_AWS_20']
        report = runner.run(root_folder=None, external_checks_dir=None, files=[file_rel_path],
                            runner_filter=RunnerFilter(framework='terraform', checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks

        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something

        for record in all_checks:
            # no need to join with a '/' because the TF runner adds it to the start of the file path
            self.assertEqual(record.repo_file_path, f'/{file_rel_path}')

    def test_record_relative_path_with_abs_file(self):

        # test whether the record's repo_file_path is correct, relative to the CWD (with a / at the start).

        # this is just constructing the scan dir as normal
        current_dir = os.path.dirname(os.path.realpath(__file__))
        scan_file_path = os.path.join(current_dir, "resources", "nested_dir", "nested", "example.tf")

        file_rel_path = os.path.relpath(scan_file_path)
        file_abs_path = os.path.abspath(scan_file_path)

        runner = Runner()
        checks_allowlist = ['CKV_AWS_20']
        report = runner.run(root_folder=None, external_checks_dir=None, files=[file_abs_path],
                            runner_filter=RunnerFilter(framework='terraform', checks=checks_allowlist))

        all_checks = report.failed_checks + report.passed_checks

        self.assertGreater(len(all_checks), 0)  # ensure that the assertions below are going to do something

        for record in all_checks:
            # no need to join with a '/' because the TF runner adds it to the start of the file path
            self.assertEqual(record.repo_file_path, f'/{file_rel_path}')

    def test_runner_malformed_857(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        passing_tf_file_path = current_dir + "/resources/malformed_857/main.tf"

        runner = Runner()
        runner.run(root_folder=None, external_checks_dir=None, files=[passing_tf_file_path])
        # If we get here all is well. :-)  Failure would throw an exception.

    def test_runner_empty_locals(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        passing_tf_file_path = current_dir + "/resources/empty_locals"

        runner = Runner()
        r = runner.run(root_folder=passing_tf_file_path, external_checks_dir=None)

        assert len(r.parsing_errors) == 0

    def test_module_skip(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        report = Runner().run(root_folder=f"{current_dir}/resources/module_skip",
                              external_checks_dir=None,
                              runner_filter=RunnerFilter(checks="CKV_AWS_19"))  # bucket encryption

        self.assertEqual(len(report.skipped_checks), 5)
        self.assertEqual(len(report.failed_checks), 0)
        self.assertEqual(len(report.passed_checks), 0)

        found_inside = False
        found_outside = False

        for record in report.failed_checks:
            if "inside" in record.resource:
                found_inside = True
                print(record)
                self.assertEqual(record.resource, "module.test_module.aws_s3_bucket.inside")
                assert record.file_path == "/module/module.tf"
                self.assertEqual(record.file_line_range, [7, 9])
                assert record.caller_file_path == "/main.tf"
                # ATTENTION!! If this breaks, see the "HACK ALERT" comment in runner.run_block.
                #             A bug might have been fixed.
                self.assertEqual(record.caller_file_line_range, [6, 8])

            if "outside" in record.resource:
                found_outside = True
                self.assertEqual(record.resource, "aws_s3_bucket.outside")
                assert record.file_path == "/main.tf"
                self.assertEqual(record.file_line_range, [12, 16])
                self.assertIsNone(record.caller_file_path)
                self.assertIsNone(record.caller_file_line_range)

        self.assertFalse(found_inside)
        self.assertFalse(found_outside)

    def test_module_failure_reporting_772(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        report = Runner().run(root_folder=f"{current_dir}/resources/module_failure_reporting_772",
                              external_checks_dir=None,
                              runner_filter=RunnerFilter(checks="CKV_AWS_19"))  # bucket encryption

        self.assertEqual(len(report.failed_checks), 2)
        self.assertEqual(len(report.passed_checks), 0)

        found_inside = False
        found_outside = False
        for record in report.failed_checks:
            # "outside" bucket (not defined in a module) should be a direct resource path and
            # should not have caller file info.
            if "outside" in record.resource:
                found_outside = True
                self.assertEqual(record.resource, "aws_s3_bucket.outside")
                assert record.file_path == "/main.tf"
                self.assertEqual(record.file_line_range, [11, 13])
                self.assertIsNone(record.caller_file_path)
                self.assertIsNone(record.caller_file_line_range)

            if "inside" in record.resource:
                found_inside = True
                self.assertEqual(record.resource, "module.test_module.aws_s3_bucket.inside")
                assert record.file_path == "/module/module.tf"
                self.assertEqual(record.file_line_range, [7, 9])
                assert record.caller_file_path == "/main.tf"
                # ATTENTION!! If this breaks, see the "HACK ALERT" comment in runner.run_block.
                #             A bug might have been fixed.
                self.assertEqual(record.caller_file_line_range, [6, 8])

        self.assertTrue(found_inside)
        self.assertTrue(found_outside)


    def test_loading_external_checks_yaml(self):
        runner = Runner()
        runner.graph_registry.checks = []
        runner.graph_registry.load_checks()
        base_len = len(runner.graph_registry.checks)
        current_dir = os.path.dirname(os.path.realpath(__file__))
        extra_checks_dir_path = current_dir + "/extra_yaml_checks"
        runner.load_external_checks([extra_checks_dir_path])
        self.assertEqual(len(runner.graph_registry.checks), base_len + 2)
        runner.graph_registry.checks = runner.graph_registry.checks[:base_len]

    def test_loading_external_checks_yaml_multiple_times(self):
        runner = Runner()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        runner.graph_registry.checks = []
        extra_checks_dir_path = [current_dir + "/extra_yaml_checks"]
        runner.load_external_checks(extra_checks_dir_path)
        self.assertEqual(len(runner.graph_registry.checks), 2)
        runner.load_external_checks(extra_checks_dir_path)
        self.assertEqual(len(runner.graph_registry.checks), 2)
        self.assertIn('CUSTOM_GRAPH_AWS_1', [x.id for x in runner.graph_registry.checks])
        self.assertIn('CKV2_CUSTOM_1', [x.id for x in runner.graph_registry.checks])
        runner.graph_registry.checks = []

    def test_loading_external_checks_python(self):
        runner = Runner()
        from tests.terraform.runner.extra_checks.S3EnvironmentCheck import scanner
        current_dir = os.path.dirname(os.path.realpath(__file__))
        extra_checks_dir_paths = [current_dir + "/extra_checks"]
        runner.load_external_checks(extra_checks_dir_paths)
        found = 0
        for resource_type in scanner.supported_resources:
            checks = resource_registry.checks[resource_type]
            self.assertIn(scanner, checks)
            found += 1
        self.assertEqual(found, len(scanner.supported_resources))

    def test_loading_external_checks_python_multiple_times(self):
        runner = Runner()
        from tests.terraform.runner.extra_checks.S3EnvironmentCheck import scanner
        current_dir = os.path.dirname(os.path.realpath(__file__))
        extra_checks_dir_paths = [current_dir + "/extra_checks", current_dir + "/extra_checks"]
        runner.load_external_checks(extra_checks_dir_paths)
        found = 0
        for resource_type in scanner.supported_resources:
            checks = resource_registry.checks[resource_type]
            self.assertIn(scanner, checks)
            instances = list(filter(lambda c: c.id == scanner.id, checks))
            self.assertEqual(len(instances), 1)
            found += 1

        self.assertEqual(found, len(scanner.supported_resources))

    def test_loading_external_checks_python_and_yaml(self):
        runner = Runner()
        from tests.terraform.runner.extra_checks.S3EnvironmentCheck import scanner
        current_dir = os.path.dirname(os.path.realpath(__file__))
        extra_checks_dir_paths = [current_dir + "/extra_checks", current_dir + "/extra_yaml_checks"]
        runner.load_external_checks(extra_checks_dir_paths)
        found = 0
        for resource_type in scanner.supported_resources:
            checks = resource_registry.checks[resource_type]
            self.assertIn(scanner, checks)
            found += 1
        self.assertEqual(found, len(scanner.supported_resources))
        self.assertEqual(len(list(filter(lambda c: c.id == CUSTOM_GRAPH_CHECK_ID, runner.graph_registry.checks))), 1)
        # Remove external checks from registry.
        runner.graph_registry.checks[:] = [check for check in runner.graph_registry.checks if "CUSTOM" not in check.id]

    def test_wrong_check_imports(self):
        wrong_imports = ["arm", "cloudformation", "dockerfile", "helm", "kubernetes", "serverless"]
        check_imports = []

        checks_path = Path(inspect.getfile(Runner)).parent.joinpath("checks")
        for file in checks_path.rglob("*.py"):
            with file.open() as f:
                instructions = dis.get_instructions(f.read())
                import_names = [instr.argval for instr in instructions if "IMPORT_NAME" == instr.opname]

                for import_name in import_names:
                    wrong_import = next((import_name for x in wrong_imports if x in import_name), None)
                    if wrong_import:
                        check_imports.append({file.name: wrong_import})

        assert len(check_imports) == 0, f"Wrong imports were added: {check_imports}"

    def test_entity_context_fetching(self):
        runner = Runner()
        runner.context = {'/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf': {'module': {'module': {'vpc': {'start_line': 1, 'end_line': 7, 'code_lines': [(1, 'module "vpc" {\n'), (2, '  source       = "../../"\n'), (3, '  cidr         = var.cidr\n'), (4, '  zone         = var.zone\n'), (5, '  common_tags  = var.common_tags\n'), (6, '  account_name = var.account_name\n'), (7, '}\n')], 'skipped_checks': []}}}}, '/mock/os/terraform-aws-vpc/example/examplea/provider.aws.tf': {'provider': {'aws': {'default': {'start_line': 1, 'end_line': 3, 'code_lines': [(1, 'provider "aws" {\n'), (2, '  region = "eu-west-2"\n'), (3, '}\n')], 'skipped_checks': []}}}}, '/mock/os/terraform-aws-vpc/example/examplea/variables.tf': {'variable': {'cidr': {'start_line': 1, 'end_line': 3, 'code_lines': [(1, 'variable "cidr" {\n'), (2, '  type = string\n'), (3, '}\n')], 'skipped_checks': []}, 'zone': {'start_line': 5, 'end_line': 7, 'code_lines': [(5, 'variable "zone" {\n'), (6, '  type = list(any)\n'), (7, '}\n')], 'skipped_checks': []}, 'account_name': {'start_line': 9, 'end_line': 11, 'code_lines': [(9, 'variable "account_name" {\n'), (10, '  type = string\n'), (11, '}\n')], 'skipped_checks': []}, 'common_tags': {'start_line': 13, 'end_line': 15, 'code_lines': [(13, 'variable "common_tags" {\n'), (14, '  type = map(any)\n'), (15, '}\n')], 'skipped_checks': []}}}, '/mock/os/terraform-aws-vpc/aws_eip.nateip.tf[/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf#0]': {'resource': {'aws_eip': {'nateip': {'start_line': 1, 'end_line': 4, 'code_lines': [(1, 'resource "aws_eip" "nateip" {\n'), (2, '  count = var.subnets\n'), (3, '  tags  = var.common_tags\n'), (4, '}\n')], 'skipped_checks': []}}}}, '/mock/os/terraform-aws-vpc/aws_internet_gateway.gw.tf[/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf#0]': {'resource': {'aws_internet_gateway': {'gw': {'start_line': 1, 'end_line': 6, 'code_lines': [(1, 'resource "aws_internet_gateway" "gw" {\n'), (2, '  vpc_id = aws_vpc.main.id\n'), (3, '\n'), (4, '  tags = merge(var.common_tags,\n'), (5, '  tomap({ "Name" = "${upper(var.account_name)}-IGW" }))\n'), (6, '}\n')], 'skipped_checks': []}}}}, '/mock/os/terraform-aws-vpc/aws_nat_gateway.natgateway.tf[/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf#0]': {'resource': {'aws_nat_gateway': {'natgateway': {'start_line': 1, 'end_line': 8, 'code_lines': [(1, 'resource "aws_nat_gateway" "natgateway" {\n'), (2, '  count         = var.subnets\n'), (3, '  allocation_id = element(aws_eip.nateip.*.id, count.index)\n'), (4, '  depends_on    = [aws_internet_gateway.gw]\n'), (5, '  subnet_id     = element(aws_subnet.public.*.id, count.index)\n'), (6, '  tags = merge(var.common_tags,\n'), (7, '  tomap({ "Name" = "${upper(var.account_name)}-AZ${count.index + 1}" }))\n'), (8, '}\n')], 'skipped_checks': []}}}}, '/mock/os/terraform-aws-vpc/aws_network_acl.NetworkAclPrivate.tf[/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf#0]': {'resource': {'aws_network_acl': {'networkaclprivate': {'start_line': 1, 'end_line': 25, 'code_lines': [(1, 'resource "aws_network_acl" "networkaclprivate" {\n'), (2, '  vpc_id     = aws_vpc.main.id\n'), (3, '  subnet_ids = aws_subnet.private.*.id\n'), (4, '\n'), (5, '  egress {\n'), (6, '    rule_no    = 100\n'), (7, '    action     = "allow"\n'), (8, '    cidr_block = "0.0.0.0/0"\n'), (9, '    from_port  = 0\n'), (10, '    to_port    = 0\n'), (11, '    protocol   = "all"\n'), (12, '  }\n'), (13, '\n'), (14, '  ingress {\n'), (15, '    rule_no    = 100\n'), (16, '    action     = "allow"\n'), (17, '    cidr_block = "0.0.0.0/0"\n'), (18, '    from_port  = 0\n'), (19, '    to_port    = 0\n'), (20, '    protocol   = "all"\n'), (21, '  }\n'), (22, '\n'), (23, '  tags = merge(var.common_tags,\n'), (24, '  tomap({ "Name" = "${var.account_name}-NetworkAcl-Private" }))\n'), (25, '}\n')], 'skipped_checks': []}}}}, '/mock/os/terraform-aws-vpc/aws_network_acl.NetworkAclPublic.tf[/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf#0]': {'resource': {'aws_network_acl': {'networkaclpublic': {'start_line': 1, 'end_line': 25, 'code_lines': [(1, 'resource "aws_network_acl" "networkaclpublic" {\n'), (2, '  vpc_id     = aws_vpc.main.id\n'), (3, '  subnet_ids = aws_subnet.public.*.id\n'), (4, '\n'), (5, '  egress {\n'), (6, '    rule_no    = 100\n'), (7, '    action     = "allow"\n'), (8, '    cidr_block = "0.0.0.0/0"\n'), (9, '    from_port  = 0\n'), (10, '    to_port    = 0\n'), (11, '    protocol   = "all"\n'), (12, '  }\n'), (13, '\n'), (14, '  ingress {\n'), (15, '    rule_no    = 100\n'), (16, '    action     = "allow"\n'), (17, '    cidr_block = "0.0.0.0/0"\n'), (18, '    from_port  = 0\n'), (19, '    to_port    = 0\n'), (20, '    protocol   = "all"\n'), (21, '  }\n'), (22, '\n'), (23, '  tags = merge(var.common_tags,\n'), (24, '  tomap({ "Name" = "${var.account_name}-NetworkAcl-Public" }))\n'), (25, '}\n')], 'skipped_checks': []}}}}, '/mock/os/terraform-aws-vpc/aws_route_table.private.tf[/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf#0]': {'resource': {'aws_route_table': {'private': {'start_line': 1, 'end_line': 8, 'code_lines': [(1, 'resource "aws_route_table" "private" {\n'), (2, '  vpc_id = aws_vpc.main.id\n'), (3, '\n'), (4, '  propagating_vgws = [aws_vpn_gateway.vpn_gw.id]\n'), (5, '\n'), (6, '  tags = merge(var.common_tags,\n'), (7, '  tomap({ "Name" = "${var.account_name}-Private-${element(aws_subnet.private.*.id, 0)}" }))\n'), (8, '}\n')], 'skipped_checks': []}}, 'aws_route': {'private': {'start_line': 10, 'end_line': 14, 'code_lines': [(10, 'resource "aws_route" "private" {\n'), (11, '  route_table_id         = aws_route_table.private.id\n'), (12, '  destination_cidr_block = "0.0.0.0/0"\n'), (13, '  nat_gateway_id         = element(aws_nat_gateway.natgateway.*.id, 0)\n'), (14, '}\n')], 'skipped_checks': []}}}}, '/mock/os/terraform-aws-vpc/aws_route_table.public.tf[/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf#0]': {'resource': {'aws_route_table': {'public': {'start_line': 1, 'end_line': 6, 'code_lines': [(1, 'resource "aws_route_table" "public" {\n'), (2, '  vpc_id = aws_vpc.main.id\n'), (3, '\n'), (4, '  tags = merge(var.common_tags,\n'), (5, '  tomap({ "Name" = "${upper(var.account_name)}-Public" }))\n'), (6, '}\n')], 'skipped_checks': []}}, 'aws_route': {'public': {'start_line': 8, 'end_line': 12, 'code_lines': [(8, 'resource "aws_route" "public" {\n'), (9, '  route_table_id         = aws_route_table.public.id\n'), (10, '  destination_cidr_block = "0.0.0.0/0"\n'), (11, '  gateway_id             = aws_internet_gateway.gw.id\n'), (12, '}\n')], 'skipped_checks': []}}}}, '/mock/os/terraform-aws-vpc/aws_route_table_association.private.tf[/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf#0]': {'resource': {'aws_route_table_association': {'private': {'start_line': 1, 'end_line': 5, 'code_lines': [(1, 'resource "aws_route_table_association" "private" {\n'), (2, '  count          = var.subnets\n'), (3, '  subnet_id      = element(aws_subnet.private.*.id, count.index)\n'), (4, '  route_table_id = aws_route_table.private.id\n'), (5, '}\n')], 'skipped_checks': []}}}}, '/mock/os/terraform-aws-vpc/aws_route_table_association.public.tf[/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf#0]': {'resource': {'aws_route_table_association': {'public': {'start_line': 1, 'end_line': 5, 'code_lines': [(1, 'resource "aws_route_table_association" "public" {\n'), (2, '  count          = var.subnets\n'), (3, '  subnet_id      = element(aws_subnet.public.*.id, count.index)\n'), (4, '  route_table_id = aws_route_table.public.id\n'), (5, '}\n')], 'skipped_checks': []}}}}, '/mock/os/terraform-aws-vpc/aws_subnet.private.tf[/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf#0]': {'resource': {'aws_subnet': {'private': {'start_line': 1, 'end_line': 10, 'code_lines': [(1, 'resource "aws_subnet" "private" {\n'), (2, '  count             = var.subnets\n'), (3, '  vpc_id            = aws_vpc.main.id\n'), (4, '  cidr_block        = local.private_cidrs[count.index]\n'), (5, '  availability_zone = data.aws_availability_zones.available.names[count.index]\n'), (6, '\n'), (7, '  tags = merge(var.common_tags,\n'), (8, '    tomap({ "Type" = "Private" }),\n'), (9, '  tomap({ "Name" = "${upper(var.account_name)}-Private-${var.zone[count.index]}" }))\n'), (10, '}\n')], 'skipped_checks': []}}}}, '/mock/os/terraform-aws-vpc/aws_subnet.public.tf[/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf#0]': {'resource': {'aws_subnet': {'public': {'start_line': 1, 'end_line': 10, 'code_lines': [(1, 'resource "aws_subnet" "public" {\n'), (2, '  count             = var.subnets\n'), (3, '  vpc_id            = aws_vpc.main.id\n'), (4, '  cidr_block        = local.public_cidrs[count.index]\n'), (5, '  availability_zone = data.aws_availability_zones.available.names[count.index]\n'), (6, '\n'), (7, '  tags = merge(var.common_tags,\n'), (8, '    tomap({ "Type" = "Public" }),\n'), (9, '  tomap({ "Name" = "${upper(var.account_name)}-Public-${var.zone[count.index]}" }))\n'), (10, '}\n')], 'skipped_checks': []}}}}, '/mock/os/terraform-aws-vpc/aws_vpc.main.tf[/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf#0]': {'locals': {'start_line': 10, 'end_line': 12, 'code_lines': [(10, 'locals {\n'), (11, '  tags = merge(var.common_tags, tomap({ "Name" = upper(var.account_name) }))\n'), (12, '}\n')], 'assignments': {'tags': "merge([],tomap({'Name':'upper(test)'}))"}, 'skipped_checks': []}, 'resource': {'aws_vpc': {'main': {'start_line': 1, 'end_line': 7, 'code_lines': [(1, 'resource "aws_vpc" "main" {\n'), (2, '  cidr_block           = var.cidr\n'), (3, '  enable_dns_support   = true\n'), (4, '  enable_dns_hostnames = true\n'), (5, '\n'), (6, '  tags = local.tags\n'), (7, '}\n')], 'skipped_checks': []}}}}, '/mock/os/terraform-aws-vpc/aws_vpn_gateway.vpn_gw.tf[/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf#0]': {'resource': {'aws_vpn_gateway': {'vpn_gw': {'start_line': 1, 'end_line': 6, 'code_lines': [(1, 'resource "aws_vpn_gateway" "vpn_gw" {\n'), (2, '  vpc_id = aws_vpc.main.id\n'), (3, '\n'), (4, '  tags = merge(var.common_tags,\n'), (5, '  tomap({ "Name" = "${upper(var.account_name)}-VGW" }))\n'), (6, '}\n')], 'skipped_checks': []}}}}, '/mock/os/terraform-aws-vpc/data.aws_availability_zones.tf[/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf#0]': {'data': {'aws_availability_zones': {'available': {'start_line': 1, 'end_line': 0, 'code_lines': [], 'skipped_checks': []}}}}, '/mock/os/terraform-aws-vpc/variables.tf[/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf#0]': {'locals': {'start_line': 27, 'end_line': 30, 'code_lines': [(27, 'locals {\n'), (28, '  public_cidrs  = [cidrsubnet(var.cidr, 3, 0), cidrsubnet(var.cidr, 3, 1), cidrsubnet(var.cidr, 3, 2)]\n'), (29, '  private_cidrs = [cidrsubnet(var.cidr, 3, 3), cidrsubnet(var.cidr, 3, 4), cidrsubnet(var.cidr, 3, 5)]\n'), (30, '}\n')], 'skipped_checks': []}, 'variable': {'account_name': {'start_line': 1, 'end_line': 4, 'code_lines': [(1, 'variable "account_name" {\n'), (2, '  type        = string\n'), (3, '  description = "The Name of the Account"\n'), (4, '}\n')], 'skipped_checks': []}, 'cidr': {'start_line': 6, 'end_line': 9, 'code_lines': [(6, 'variable "cidr" {\n'), (7, '  type        = string\n'), (8, '  description = "The range to be associated with the VPC and cleaved into the subnets"\n'), (9, '}\n')], 'skipped_checks': []}, 'common_tags': {'start_line': 11, 'end_line': 14, 'code_lines': [(11, 'variable "common_tags" {\n'), (12, '  type        = map(any)\n'), (13, '  description = "A tagging scheme"\n'), (14, '}\n')], 'skipped_checks': []}, 'zone': {'start_line': 16, 'end_line': 19, 'code_lines': [(16, 'variable "zone" {\n'), (17, '  type        = list(any)\n'), (18, '  description = "Availability zone names"\n'), (19, '}\n')], 'skipped_checks': []}, 'subnets': {'start_line': 21, 'end_line': 25, 'code_lines': [(21, 'variable "subnets" {\n'), (22, '  type        = number\n'), (23, '  default     = 3\n'), (24, '  description = "The number of subnets required, less than or equal to the number of availability zones"\n'), (25, '}\n')], 'skipped_checks': []}, 'assignments': {'subnets': 3}}}}
        entity_with_non_found_path = {'block_name_': 'aws_vpc.main', 'block_type_': 'resource', 'file_path_': '/mock/os/terraform-aws-vpc/aws_vpc.main.tf', 'config_': {'aws_vpc': {'main': {'cidr_block': ['10.0.0.0/21'], 'enable_dns_hostnames': [True], 'enable_dns_support': [True], 'tags': ["merge([],tomap({'Name':'upper(test)'}))"]}}}, 'label_': 'BlockType.RESOURCE: aws_vpc.main', 'id_': 'aws_vpc.main', 'source_': 'Terraform', 'cidr_block': '10.0.0.0/21', 'enable_dns_hostnames': True, 'enable_dns_support': True, 'tags': "merge([],tomap({'Name':'upper(test)'}))", 'resource_type': 'aws_vpc', 'rendering_breadcrumbs_': {'cidr_block': [{'type': 'module', 'name': 'vpc', 'path': '/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf', 'module_connection': False}, {'type': 'variable', 'name': 'cidr', 'path': '/mock/os/terraform-aws-vpc/variables.tf', 'module_connection': False}, {'type': 'locals', 'name': 'private_cidrs', 'path': '/mock/os/terraform-aws-vpc/variables.tf', 'module_connection': False}, {'type': 'locals', 'name': 'public_cidrs', 'path': '/mock/os/terraform-aws-vpc/variables.tf', 'module_connection': False}, {'type': 'locals', 'name': 'private_cidrs', 'path': '/mock/os/terraform-aws-vpc/variables.tf', 'module_connection': False}, {'type': 'locals', 'name': 'public_cidrs', 'path': '/mock/os/terraform-aws-vpc/variables.tf', 'module_connection': False}, {'type': 'output', 'name': 'private_cidrs', 'path': '/mock/os/terraform-aws-vpc/outputs.tf', 'module_connection': False}], 'source_module_': [{'type': 'module', 'name': 'vpc', 'path': '/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf'}], 'tags': [{'type': 'module', 'name': 'vpc', 'path': '/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf', 'module_connection': False}, {'type': 'variable', 'name': 'account_name', 'path': '/mock/os/terraform-aws-vpc/variables.tf', 'module_connection': False}, {'type': 'locals', 'name': 'tags', 'path': '/mock/os/terraform-aws-vpc/aws_vpc.main.tf', 'module_connection': False}]}, 'hash': 'bac3bb7d21610be9ad786c1e9b5a2b3f6f13e60699fa935b32bb1f9f10a792e4'}
        entity_context, entity_evaluations = runner.get_entity_context_and_evaluations(entity_with_non_found_path)

        assert entity_context is not None
        assert entity_context['start_line'] == 1 and entity_context['end_line']==7

        entity_with_found_path = {'block_name_': 'aws_vpc.main', 'block_type_': 'resource', 'file_path_': '/mock/os/terraform-aws-vpc/aws_vpc.main.tf[/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf#0]', 'config_': {'aws_vpc': {'main': {'cidr_block': ['10.0.0.0/21'], 'enable_dns_hostnames': [True], 'enable_dns_support': [True], 'tags': ["merge([],tomap({'Name':'upper(test)'}))"]}}}, 'label_': 'BlockType.RESOURCE: aws_vpc.main', 'id_': 'aws_vpc.main', 'source_': 'Terraform', 'cidr_block': '10.0.0.0/21', 'enable_dns_hostnames': True, 'enable_dns_support': True, 'tags': "merge([],tomap({'Name':'upper(test)'}))", 'resource_type': 'aws_vpc', 'rendering_breadcrumbs_': {'cidr_block': [{'type': 'module', 'name': 'vpc', 'path': '/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf', 'module_connection': False}, {'type': 'variable', 'name': 'cidr', 'path': '/mock/os/terraform-aws-vpc/variables.tf', 'module_connection': False}, {'type': 'locals', 'name': 'private_cidrs', 'path': '/mock/os/terraform-aws-vpc/variables.tf', 'module_connection': False}, {'type': 'locals', 'name': 'public_cidrs', 'path': '/mock/os/terraform-aws-vpc/variables.tf', 'module_connection': False}, {'type': 'locals', 'name': 'private_cidrs', 'path': '/mock/os/terraform-aws-vpc/variables.tf', 'module_connection': False}, {'type': 'locals', 'name': 'public_cidrs', 'path': '/mock/os/terraform-aws-vpc/variables.tf', 'module_connection': False}, {'type': 'output', 'name': 'private_cidrs', 'path': '/mock/os/terraform-aws-vpc/outputs.tf', 'module_connection': False}], 'source_module_': [{'type': 'module', 'name': 'vpc', 'path': '/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf'}], 'tags': [{'type': 'module', 'name': 'vpc', 'path': '/mock/os/terraform-aws-vpc/example/examplea/module.vpc.tf', 'module_connection': False}, {'type': 'variable', 'name': 'account_name', 'path': '/mock/os/terraform-aws-vpc/variables.tf', 'module_connection': False}, {'type': 'locals', 'name': 'tags', 'path': '/mock/os/terraform-aws-vpc/aws_vpc.main.tf', 'module_connection': False}]}, 'hash': 'bac3bb7d21610be9ad786c1e9b5a2b3f6f13e60699fa935b32bb1f9f10a792e4'}
        entity_context, entity_evaluations = runner.get_entity_context_and_evaluations(entity_with_found_path)

        assert entity_context is not None
        assert entity_context['start_line'] == 1 and entity_context['end_line']==7

    def test_resource_values_dont_exist(self):
        resources_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "resources", "resource_value_without_var")
        checks_allow_list = ['CKV_AWS_21']
        skip_checks = ['CUSTOM_AWS_1']
        source_files = ["main.tf", "variables.tf"]

        runner = Runner()
        report = runner.run(root_folder=None, external_checks_dir=None,
                            files=list(map(lambda f: f'{resources_path}/{f}', source_files)),
                            runner_filter=RunnerFilter(framework='terraform',
                                                       checks=checks_allow_list, skip_checks=skip_checks))

        self.assertEqual(len(report.passed_checks), 1)
        self.assertEqual(len(report.failed_checks), 1)

    def test_resource_values_do_exist(self):
        resources_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "resources", "resource_value_without_var")
        checks_allow_list = ['CKV_AWS_21']
        skip_checks = ['CUSTOM_AWS_1']
        source_files = ["main.tf", "variables.tf", "variables_unscoped.tf"]

        runner = Runner()
        report = runner.run(root_folder=None, external_checks_dir=None,
                            files=list(map(lambda f: f'{resources_path}/{f}', source_files)),
                            runner_filter=RunnerFilter(framework='terraform',
                                                       checks=checks_allow_list, skip_checks=skip_checks))

        self.assertEqual(len(report.passed_checks), 3)
        self.assertEqual(len(report.failed_checks), 3)

    def test_resource_negative_values_dont_exist(self):
        resources_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "resources", "resource_negative_value_without_var")
        checks_allow_list = ['CKV_AWS_57']
        skip_checks = ['CUSTOM_AWS_1']
        source_files = ["main.tf", "variables.tf"]

        runner = Runner()
        report = runner.run(root_folder=None, external_checks_dir=None,
                            files=list(map(lambda f: f'{resources_path}/{f}', source_files)),
                            runner_filter=RunnerFilter(framework='terraform',
                                                       checks=checks_allow_list, skip_checks=skip_checks))

        self.assertEqual(len(report.passed_checks), 1)
        self.assertEqual(len(report.failed_checks), 1)

    def test_resource_negative_values_do_exist(self):
        resources_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "resources", "resource_negative_value_without_var")
        checks_allow_list = ['CKV_AWS_57']
        skip_checks = ['CUSTOM_AWS_1']
        source_files = ["main.tf", "variables.tf", "variables_unscoped.tf"]

        runner = Runner()
        report = runner.run(root_folder=None, external_checks_dir=None,
                            files=list(map(lambda f: f'{resources_path}/{f}', source_files)),
                            runner_filter=RunnerFilter(framework='terraform',
                                                       checks=checks_allow_list, skip_checks=skip_checks))

        self.assertEqual(len(report.passed_checks), 3)
        self.assertEqual(len(report.failed_checks), 3)

    def test_no_duplicate_results(self):
        resources_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "resources", "duplicate_violations")
        runner = Runner()
        report = runner.run(root_folder=resources_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='terraform'))

        unique_checks = []
        for record in report.passed_checks:
            check_unique = f"{record.check_id}.{record.resource}"
            if check_unique in unique_checks:
                self.fail(f"found duplicate results in report: {record.to_string()}")
            unique_checks.append(check_unique)

    def test_malformed_file_in_parsing_error(self):
        resources_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "resources", "unbalanced_eval_brackets")
        runner = Runner()
        report = runner.run(root_folder=resources_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='terraform'))
        file_path = os.path.join(resources_path, 'main.tf')
        self.assertEqual(report.parsing_errors[0], file_path)

    def test_runner_scan_hcl(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        dir_to_scan = os.path.join(current_dir, 'resources', 'tf_with_hcl_files')
        orig_value = os.getenv(SCAN_HCL_FLAG)

        os.environ[SCAN_HCL_FLAG] = 'false'
        runner = Runner()
        report = runner.run(root_folder=dir_to_scan, external_checks_dir=None, files=None)
        self.assertEqual(len(report.resources), 1)

        os.environ[SCAN_HCL_FLAG] = 'true'
        runner = Runner()
        report = runner.run(root_folder=dir_to_scan, external_checks_dir=None, files=None)
        self.assertEqual(len(report.resources), 2)

        if orig_value:
            os.environ[SCAN_HCL_FLAG] = orig_value

    def test_runner_scan_hcl_file(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        file_to_scan = os.path.join(current_dir, 'resources', 'tf_with_hcl_files', 'example_acl_fail.hcl')
        orig_value = os.getenv(SCAN_HCL_FLAG)

        os.environ[SCAN_HCL_FLAG] = 'false'
        runner = Runner()
        report = runner.run(root_folder=None, external_checks_dir=None, files=[file_to_scan])
        self.assertEqual(len(report.resources), 0)

        os.environ[SCAN_HCL_FLAG] = 'true'
        runner = Runner()
        report = runner.run(root_folder=None, external_checks_dir=None, files=[file_to_scan])
        self.assertEqual(len(report.resources), 1)

        if orig_value:
            os.environ[SCAN_HCL_FLAG] = orig_value

    def tearDown(self):
        parser_registry.context = {}


if __name__ == '__main__':
    unittest.main()

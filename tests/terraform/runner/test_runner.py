import os
import unittest

import dpath.util

from checkov.runner_filter import RunnerFilter
from checkov.terraform.context_parsers.registry import parser_registry
from checkov.terraform.runner import Runner
from checkov.common.output.report import Report
from checkov.terraform.parser import Parser


class TestRunnerValid(unittest.TestCase):

    def test_runner_two_checks_only(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/example"
        runner = Runner()
        checks_allowlist = ['CKV_AWS_41', 'CKV_AZURE_1']
        report = runner.run(root_folder=valid_dir_path, external_checks_dir=None,
                            runner_filter=RunnerFilter(framework='all', checks=checks_allowlist))
        report_json = report.get_json()
        self.assertTrue(isinstance(report_json, str))
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suites())
        self.assertEqual(report.get_exit_code(soft_fail=False), 1)
        self.assertEqual(report.get_exit_code(soft_fail=True), 0)
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
        self.assertTrue(isinstance(report_json, str))
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
        self.assertTrue(isinstance(report_json, str))
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
        report.print_junit_xml()
        report.print_failed_github_md()

    def test_runner_passing_valid_tf(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        passing_tf_dir_path = current_dir + "/resources/valid_tf_only_passed_checks"

        print("testing dir" + passing_tf_dir_path)
        runner = Runner()
        report = runner.run(root_folder=passing_tf_dir_path, external_checks_dir=None)
        report_json = report.get_json()
        self.assertTrue(isinstance(report_json, str))
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suites())
        # self.assertEqual(report.get_exit_code(), 0)
        summary = report.get_summary()
        self.assertGreaterEqual(summary['passed'], 1)
        self.assertEqual(summary['failed'], 0)
        self.assertEqual(summary['skipped'], 2)
        self.assertEqual(summary["parsing_errors"], 0)

    def test_runner_specific_file(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))

        passing_tf_file_path = current_dir + "/resources/valid_tf_only_passed_checks/example.tf"

        runner = Runner()
        report = runner.run(root_folder=None, external_checks_dir=None, files=[passing_tf_file_path])
        report_json = report.get_json()
        self.assertTrue(isinstance(report_json, str))
        self.assertIsNotNone(report_json)
        self.assertIsNotNone(report.get_test_suites())
        # self.assertEqual(report.get_exit_code(), 0)
        summary = report.get_summary()
        self.assertGreaterEqual(summary['passed'], 1)
        self.assertEqual(summary['failed'], 0)
        self.assertEqual(summary["parsing_errors"], 0)

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
        self.assertEqual(len(bad_checks), 0)

    def test_no_missing_ids(self):
        runner = Runner()
        unique_checks = set()
        for registry in list(runner.block_type_registries.values()):
            checks = [check for entity_type in list(registry.checks.values()) for check in entity_type]
            for check in checks:
                unique_checks.add(check.id)
        aws_checks = list(filter(lambda check_id: '_AWS_' in check_id, unique_checks))
        for i in range(1, len(aws_checks)):
            if f'CKV_AWS_{i}' == 'CKV_AWS_4':
                # CKV_AWS_4 was deleted due to https://github.com/bridgecrewio/checkov/issues/371
                continue
            self.assertIn(f'CKV_AWS_{i}', aws_checks, msg=f'The new AWS violation should have the ID "CKV_AWS_{i}"')

        gcp_checks = list(filter(lambda check_id: '_GCP_' in check_id, unique_checks))
        for i in range(1, len(gcp_checks)):
            self.assertIn(f'CKV_GCP_{i}', gcp_checks, msg=f'The new GCP violation should have the ID "CKV_GCP_{i}"')

        azure_checks = list(filter(lambda check_id: '_AZURE_' in check_id, unique_checks))
        for i in range(1, len(azure_checks)):
            if f'CKV_AZURE_{i}' == 'CKV_AZURE_43':
                continue  # Pending merge; blocked by another issue https://github.com/bridgecrewio/checkov/pull/429

            self.assertIn(f'CKV_AZURE_{i}', azure_checks,
                          msg=f'The new Azure violation should have the ID "CKV_AZURE_{i}"')

    def test_evaluate_string_booleans(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/hcl_0.11"
        tf_file = f"{valid_dir_path}/main.tf"
        runner = Runner()
        runner.run(root_folder=valid_dir_path, external_checks_dir=None)
        runner.evaluate_string_booleans()
        print()
        self.assertEqual(
            dpath.get(runner.tf_definitions[tf_file], 'resource/0/aws_db_instance/test_db/apply_immediately/0'), True)
        self.assertEqual(
            dpath.get(runner.tf_definitions[tf_file], 'resource/0/aws_db_instance/test_db/backup_retention_period/0'),
            True)
        self.assertEqual(
            dpath.get(runner.tf_definitions[tf_file], 'resource/0/aws_db_instance/test_db/storage_encrypted/0'), False)
        self.assertEqual(dpath.get(runner.tf_definitions[tf_file], 'resource/0/aws_db_instance/test_db/multi_az/0'),
                         False)

    def test_provider_uniqueness(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        valid_dir_path = current_dir + "/resources/many_providers"
        tf_file = f"{valid_dir_path}/main.tf"
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

            def scan_resource_conf(self, conf, entity_type):
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
        tf_definitions = {}
        runner = Runner()
        parser = Parser()
        runner.tf_definitions = tf_definitions
        parser.hcl2(directory=tf_dir_path, tf_definitions=tf_definitions)
        report = Report('terraform')
        runner.check_tf_definition(root_folder=tf_dir_path, report=report, runner_filter=RunnerFilter(), external_definitions_context=external_definitions_context)
        self.assertGreaterEqual(len(report.passed_checks), 1)

    def tearDown(self):
        parser_registry.definitions_context = {}


if __name__ == '__main__':
    unittest.main()

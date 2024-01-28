import json
import os
from unittest import TestCase, mock
from parameterized import parameterized_class

from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.db_connectors.rustworkx.rustworkx_db_connector import RustworkxConnector
from checkov.terraform.runner import Runner

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))

@parameterized_class([
   {"db_connector": NetworkxConnector},
   {"db_connector": RustworkxConnector}
])
class TestGraphBuilder(TestCase):
    @mock.patch.dict(os.environ, {"CHECKOV_NEW_TF_PARSER": "False"})
    def test_build_graph(self):
        resources_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "graph_files_test")
        source_files = ["pass_s3.tf", "variables.tf"]
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(None, None, files=list(map(lambda f: f'{resources_path}/{f}', source_files)))
        tf_definitions = runner.definitions
        self.assertEqual(5, len(report.failed_checks))
        for file, definitions in tf_definitions.items():
            if file.file_path.endswith('pass_s3.tf'):
                s3_bucket_config = definitions['resource'][0]['aws_s3_bucket']['bucket_with_versioning']
                # Evaluation succeeded for included vars
                self.assertTrue(s3_bucket_config['versioning'][0]['enabled'][0])
                # Evaluation does not run for un-included vars
                self.assertEqual(s3_bucket_config['server_side_encryption_configuration'][0]['rule'][0]['apply_server_side_encryption_by_default'][0]['sse_algorithm'][0], 'var.encryption')

    def test_build_graph_new_tf_module(self):
        resources_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "graph_files_test")
        source_files = ["pass_s3.tf", "variables.tf"]
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(None, None, files=list(map(lambda f: f'{resources_path}/{f}', source_files)))
        tf_definitions = runner.definitions
        self.assertEqual(5, len(report.failed_checks))
        for file, definitions in tf_definitions.items():
            if file.file_path.endswith('pass_s3.tf'):
                s3_bucket_config = definitions['resource'][0]['aws_s3_bucket']['bucket_with_versioning']
                # Evaluation succeeded for included vars
                self.assertTrue(s3_bucket_config['versioning'][0]['enabled'][0])
                # Evaluation does not run for un-included vars
                self.assertEqual(s3_bucket_config['server_side_encryption_configuration'][0]['rule'][0]['apply_server_side_encryption_by_default'][0]['sse_algorithm'][0], 'var.encryption')

    def test_run_clean(self):
        resources_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "graph_files_test")
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=resources_path)
        self.assertEqual(6, len(report.failed_checks))
        self.assertEqual(5, len(report.passed_checks))
        self.assertEqual(0, len(report.skipped_checks))

    def test_module_and_variables(self):
        resources_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "modules-and-vars")
        runner = Runner(db_connector=self.db_connector())
        report = runner.run(root_folder=resources_path)
        self.assertLessEqual(2, len(report.failed_checks))
        self.assertLessEqual(12, len(report.passed_checks))
        self.assertEqual(0, len(report.skipped_checks))

        found_versioning_failure = False

        for record in report.failed_checks:
            if record.check_id != 'CKV_AWS_40':
                self.assertIsNotNone(record.breadcrumbs)
            if record.check_id == 'CKV_AWS_21':
                found_versioning_failure = True
                bc = record.breadcrumbs.get('versioning.enabled')
                self.assertEqual(len(bc), 2)
                bc = bc[0]
                self.assertEqual(bc.get('type'), 'module')
                self.assertEqual(os.path.relpath(bc.get('path'), resources_path), 'examples/complete/main.tf')
                self.assertEqual(record.resource, 'module.s3_bucket.aws_s3_bucket.default')

        self.assertTrue(found_versioning_failure)

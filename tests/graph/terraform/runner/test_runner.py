import os
from unittest import TestCase

from checkov.graph.terraform.runner import Runner

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class TestGraphBuilder(TestCase):

    def test_build_graph(self):
        resources_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "graph_files_test")
        source_files = ["pass_s3.tf", "variables.tf"]
        runner = Runner()
        report = runner.run(None, None, files=list(map(lambda f: f'{resources_path}/{f}', source_files)))
        tf_definitions = runner.tf_runner.tf_definitions
        self.assertEqual(2, len(report.failed_checks))
        for file, definitions in tf_definitions.items():
            if file.endswith('pass_s3.tf'):
                s3_bucket_config = definitions['resource'][0]['aws_s3_bucket']['bucket_with_versioning']
                # Evaluation succeeded for included vars
                self.assertTrue(s3_bucket_config['versioning'][0]['enabled'][0])
                # Evaluation does not run for un-included vars
                self.assertEqual(s3_bucket_config['server_side_encryption_configuration'][0]['rule'][0]['apply_server_side_encryption_by_default'][0]['sse_algorithm'][0], '${var.encryption}')

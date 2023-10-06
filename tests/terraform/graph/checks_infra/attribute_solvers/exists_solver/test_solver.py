import os
from parameterized import parameterized_class

from tests.graph_utils.utils import PARAMETERIZED_GRAPH_FRAMEWORKS
from tests.terraform.graph.checks_infra.test_base import TestBaseSolver

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))

@parameterized_class(PARAMETERIZED_GRAPH_FRAMEWORKS)
class ExistsSolver(TestBaseSolver):
    def setUp(self):
        self.checks_dir = TEST_DIRNAME
        super(ExistsSolver, self).setUp()

    def test_nested_attribute_exists(self):
        root_folder = '../../../resources/s3_bucket'
        check_id = "VersioningEnabledExists"
        should_pass = ['aws_s3_bucket.destination']
        should_fail = []
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_nested_attribute_doesnt_exists(self):
        root_folder = '../../../resources/s3_bucket'
        check_id = "TagEnvironmentExists"
        should_pass = []
        should_fail = ['aws_s3_bucket.destination']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_all_resources(self):
        root_folder = '../../../resources/encryption_test'
        check_id = "TagEnvironmentExistsAll"
        should_pass = []
        should_fail = ["aws_rds_cluster.rds_cluster_encrypted", "aws_rds_cluster.rds_cluster_unencrypted",
                       "aws_s3_bucket.encrypted_bucket", "aws_s3_bucket.unencrypted_bucket",
                       "aws_neptune_cluster.encrypted_neptune", "aws_neptune_cluster.unencrypted_neptune"]
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

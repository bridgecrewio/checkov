from pathlib import Path

from parameterized import parameterized_class

from tests.terraform.graph.checks_infra.test_base import TestBaseSolver

TEST_DIRNAME = Path(__file__).parent


@parameterized_class([{"graph_framework": "NETWORKX"}, {"graph_framework": "IGRAPH"}])
class ExistsSolver(TestBaseSolver):
    def setUp(self):
        self.checks_dir = str(TEST_DIRNAME)
        super().setUp()

    def test_allow_list(self):
        # given
        root_folder = TEST_DIRNAME.parents[2] / "resources/encryption_test"
        check_id = "ResourceAllowList"
        should_pass = [
            "aws_s3_bucket.encrypted_bucket",
            "aws_s3_bucket.unencrypted_bucket",
        ]
        should_fail = [
            "aws_rds_cluster.rds_cluster_encrypted",
            "aws_rds_cluster.rds_cluster_unencrypted",
            "aws_neptune_cluster.encrypted_neptune",
            "aws_neptune_cluster.unencrypted_neptune",
        ]
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        # when/then
        self.run_test(root_folder=str(root_folder), expected_results=expected_results, check_id=check_id)

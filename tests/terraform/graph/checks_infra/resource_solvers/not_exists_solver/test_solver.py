from pathlib import Path

from parameterized import parameterized_class

from tests.terraform.graph.checks_infra.test_base import TestBaseSolver

TEST_DIRNAME = Path(__file__).parent


@parameterized_class([{"graph_framework": "NETWORKX"}, {"graph_framework": "IGRAPH"}])
class TestNotExistsSolver(TestBaseSolver):
    def setUp(self):
        self.checks_dir = str(TEST_DIRNAME)
        super().setUp()

    def test_deny_list(self):
        # given
        root_folder = TEST_DIRNAME.parents[2] / "resources/encryption_test"
        check_id = "ResourceDenyList"

        should_fail = [
            "aws_s3_bucket.encrypted_bucket",
            "aws_s3_bucket.unencrypted_bucket",
        ]
        expected_results = {check_id: {"should_fail": should_fail}}

        # when/then
        self.run_test(root_folder=str(root_folder), expected_results=expected_results, check_id=check_id)

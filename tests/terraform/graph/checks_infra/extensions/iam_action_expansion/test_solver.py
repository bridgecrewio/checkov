from pathlib import Path

from parameterized import parameterized_class

from tests.terraform.graph.checks_infra.test_base import TestBaseSolver

TEST_DIRNAME = Path(__file__).parent


@parameterized_class([{"graph_framework": "NETWORKX"}, {"graph_framework": "IGRAPH"}])
class TestNotWithinSolver(TestBaseSolver):
    def setUp(self) -> None:
        self.checks_dir = str(TEST_DIRNAME)
        super().setUp()

    def test_with_extions(self) -> None:
        root_folder = "../../../resources/s3_bucket_policy"
        check_id = "ActionNotWithin"
        should_pass = []
        should_fail = ["aws_iam_policy_document.good", "aws_iam_policy_document.bad"]
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_without_extions(self) -> None:
        root_folder = "../../../resources/s3_bucket_policy"
        check_id = "ActionNotWithinWithoutExtensions"
        should_pass = ["aws_iam_policy_document.good", "aws_iam_policy_document.bad"]
        should_fail = []
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

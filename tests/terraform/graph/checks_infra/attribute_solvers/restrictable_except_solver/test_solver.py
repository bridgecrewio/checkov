import os

from parameterized import parameterized_class

from tests.graph_utils.utils import PARAMETERIZED_GRAPH_FRAMEWORKS
from tests.terraform.graph.checks_infra.test_base import TestBaseSolver

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


@parameterized_class(PARAMETERIZED_GRAPH_FRAMEWORKS)
class TestRestrictableExceptSolver(TestBaseSolver):
    def setUp(self):
        self.checks_dir = TEST_DIRNAME
        super(TestRestrictableExceptSolver, self).setUp()

    def test_restrictable_except_string_solver(self):
        root_folder = 'resources'
        check_id = "RestrictableExceptString"
        should_pass = ['aws_iam_policy.pass1']
        should_fail = ['aws_iam_policy.fail1']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_restrictable_except_list_solver(self):
        root_folder = 'resources'
        check_id = "RestrictableExceptList"
        should_pass = ['aws_iam_policy.pass1']
        should_fail = ['aws_iam_policy.fail1']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

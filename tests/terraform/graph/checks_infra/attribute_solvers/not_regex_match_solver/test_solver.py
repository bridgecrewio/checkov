import os

from parameterized import parameterized_class

from tests.terraform.graph.checks_infra.test_base import TestBaseSolver

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


@parameterized_class([
   {"graph_framework": "NETWORKX"},
   {"graph_framework": "IGRAPH"}
])
class TestRegexMatchSolver(TestBaseSolver):
    def setUp(self):
        self.checks_dir = TEST_DIRNAME
        super(TestRegexMatchSolver, self).setUp()

    def test_regex_match_solver_simple(self):
        root_folder = '../../../resources/tag_includes'
        check_id = "TagPrefix"
        should_pass = ['aws_subnet.acme_subnet']
        should_fail = ['aws_instance.some_instance']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

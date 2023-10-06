import os

from parameterized import parameterized_class

from tests.graph_utils.utils import PARAMETERIZED_GRAPH_FRAMEWORKS
from tests.terraform.graph.checks_infra.test_base import TestBaseSolver

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


@parameterized_class(PARAMETERIZED_GRAPH_FRAMEWORKS)
class TestSubsetSolver(TestBaseSolver):
    def setUp(self):
        self.checks_dir = TEST_DIRNAME
        super(TestSubsetSolver, self).setUp()

    def test_subset_solver_simple(self):
        root_folder = '../../../resources/arrays'
        check_id = "Subset1"
        should_pass = ['x.pass1', 'x.pass2', 'x.pass3', 'x.pass4']
        should_fail = ['x.fail1', 'x.fail2', 'x.fail3', 'x.fail4']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

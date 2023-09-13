import os

from parameterized import parameterized_class

from tests.graph_utils.utils import PARAMETERIZED_GRAPH_FRAMEWORKS
from tests.terraform.graph.checks_infra.test_base import TestBaseSolver

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


@parameterized_class(PARAMETERIZED_GRAPH_FRAMEWORKS)
class TestNotStartingWithSolver(TestBaseSolver):
    def setUp(self):
        self.checks_dir = TEST_DIRNAME
        super(TestNotStartingWithSolver, self).setUp()

    def test_name_starting_with(self):
        root_folder = '../../../resources/public_virtual_machines'
        check_id = "NameStartingWith"
        should_pass = ['aws_subnet.subnet_not_public_ip']
        should_fail = ['aws_subnet.subnet_public_ip']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_name_starting_with_jsonpath(self):
        root_folder = '../../../resources/public_virtual_machines'
        check_id = "NameStartingWithJsonpath"
        should_pass = ['aws_subnet.subnet_not_public_ip']
        should_fail = ['aws_subnet.subnet_public_ip']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

import os

from parameterized import parameterized_class

from tests.graph_utils.utils import PARAMETERIZED_GRAPH_FRAMEWORKS
from tests.terraform.graph.checks_infra.test_base import TestBaseSolver

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


@parameterized_class(PARAMETERIZED_GRAPH_FRAMEWORKS)
class TestNotIntersectsSolver(TestBaseSolver):
    def setUp(self):
        self.checks_dir = TEST_DIRNAME
        super(TestNotIntersectsSolver, self).setUp()

    def test_simple_array_no_intersection1(self):
        root_folder = '../../../resources/public_virtual_machines'
        check_id = "PublicVMs"
        should_pass = ['aws_default_security_group.default_security_group_closed']
        should_fail = ['aws_default_security_group.default_security_group_open']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_simple_array_no_intersection2(self):
        root_folder = '../../../resources/array_test'
        check_id = "ArrayNotIntersect"
        should_pass = ['aws_xyz.pass1', 'aws_xyz.pass2']
        should_fail = ['aws_xyz.fail2', 'aws_xyz.fail3', 'aws_xyz.pass3']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)
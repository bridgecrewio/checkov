import os

from parameterized import parameterized_class

from tests.graph_utils.utils import PARAMETERIZED_GRAPH_FRAMEWORKS
from tests.terraform.graph.checks_infra.test_base import TestBaseSolver

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


@parameterized_class(PARAMETERIZED_GRAPH_FRAMEWORKS)
class TestNotEndingWithSolver(TestBaseSolver):
    def setUp(self):
        self.checks_dir = TEST_DIRNAME
        super(TestNotEndingWithSolver, self).setUp()

    def test_ami_ending_with(self):
        root_folder = '../../../resources/public_virtual_machines'
        check_id = "AmiEndingWith"
        should_pass = ['aws_instance.with_closed_def_security_groups', 'aws_instance.with_open_security_groups', 'aws_instance.with_subnet_public', 'aws_instance.with_subnet_not_public',]
        should_fail = ['aws_instance.with_open_def_security_groups']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

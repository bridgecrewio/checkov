import os

from tests.graph.terraform.checks_infra.test_base import TestBaseSolver

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class TestStartingWithSolver(TestBaseSolver):
    def setUp(self):
        self.checks_dir = TEST_DIRNAME
        super(TestStartingWithSolver, self).setUp()

    def test_name_starting_with(self):
        root_folder = '../../../resources/public_virtual_machines'
        check_id = "NameStartingWith"
        should_pass = ['aws_subnet.subnet_public_ip']
        should_fail = ['aws_subnet.subnet_not_public_ip']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

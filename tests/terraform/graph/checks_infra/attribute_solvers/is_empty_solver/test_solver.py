import os

from tests.terraform.graph.checks_infra.test_base import TestBaseSolver

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class TestIsEmptySolver(TestBaseSolver):
    def setUp(self):
        self.checks_dir = TEST_DIRNAME
        super(TestIsEmptySolver, self).setUp()

    def test_is_empty_solver_simple(self):
        root_folder = './'
        check_id = "SGPorts"
        should_pass = ['aws_security_group.sg3']
        should_fail = ['aws_security_group.aws_security_group_public', 'aws_security_group.sg2']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

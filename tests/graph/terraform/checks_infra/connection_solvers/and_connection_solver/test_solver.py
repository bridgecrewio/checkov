import os
from tests.graph.terraform.checks_infra.test_base import TestBaseSolver

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


class ConnectionSolver(TestBaseSolver):
    def setUp(self):
        self.checks_dir = TEST_DIRNAME
        super(ConnectionSolver, self).setUp()

    def test_and_connection(self):
        root_folder = '../../../resources/ec2_instance_network_interfaces'
        check_id = "AndComplexConnection"
        should_pass = ['aws_network_interface.foo']
        should_fail = ['aws_network_interface.goo', 'aws_instance.bar', 'aws_instance.foo']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results)

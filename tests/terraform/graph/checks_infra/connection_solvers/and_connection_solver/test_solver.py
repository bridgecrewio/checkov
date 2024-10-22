import os

from parameterized import parameterized_class

from tests.graph_utils.utils import PARAMETERIZED_GRAPH_FRAMEWORKS
from tests.terraform.graph.checks_infra.test_base import TestBaseSolver

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


@parameterized_class(PARAMETERIZED_GRAPH_FRAMEWORKS)
class ConnectionSolver(TestBaseSolver):
    def setUp(self):
        self.checks_dir = TEST_DIRNAME
        super(ConnectionSolver, self).setUp()

    def test_and_connection(self):
        root_folder = '../../../resources/ec2_instance_network_interfaces'
        check_id = "AndComplexConnection"
        should_pass = ['aws_network_interface.network_interface_foo']
        should_fail = ['aws_network_interface.network_interface_goo', 'aws_instance.instance_bar', 'aws_instance.instance_foo']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_multiple_connections(self):
        root_folder = '../../../resources/lb'
        check_id = "ALBConnectedToHTTPS"
        should_pass = []
        should_fail = ["aws_lb.lb_bad_1"]
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

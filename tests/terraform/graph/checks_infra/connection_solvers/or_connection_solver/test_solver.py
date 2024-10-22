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

    def test_or_connection(self):
        root_folder = '../../../resources/ec2_instance_network_interfaces'
        check_id = "SpecificInstanceComplexConnection"
        should_pass = ['aws_instance.instance_foo', 'aws_network_interface.network_interface_foo', 'aws_instance.instance_bar']
        should_fail = ['aws_network_interface.network_interface_goo']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

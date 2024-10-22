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

    def test_connection_not_found(self):
        root_folder = '../../../checks/resources/VPCHasOneOfWantedFlowLogs'
        check_id = "VPCHasOneOfWantedFlowLogs"
        should_pass = ['aws_vpc.ok_vpc', 'aws_vpc.ok_vpc1']
        should_fail = ['aws_vpc.not_ok_vpc', 'aws_vpc.not_ok_vpc2']
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)
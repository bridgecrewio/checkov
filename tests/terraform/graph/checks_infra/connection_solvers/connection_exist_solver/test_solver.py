import os
from pathlib import Path

from parameterized import parameterized_class

from checkov.runner_filter import RunnerFilter
from tests.graph_utils.utils import PARAMETERIZED_GRAPH_FRAMEWORKS
from tests.terraform.graph.checks_infra.test_base import TestBaseSolver

TEST_DIRNAME = os.path.dirname(os.path.realpath(__file__))


@parameterized_class(PARAMETERIZED_GRAPH_FRAMEWORKS)
class ConnectionSolver(TestBaseSolver):
    def setUp(self):
        self.checks_dir = TEST_DIRNAME
        super(ConnectionSolver, self).setUp()

    def test_connection_found(self):
        root_folder = '../../../resources/ec2_instance_network_interfaces'
        check_id = "NetworkInterfaceForInstance"
        should_pass = ['aws_instance.instance_foo', 'aws_network_interface.network_interface_foo']
        should_fail = []
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_output_connection(self):
        root_folder = '../../../resources/output_example'
        check_id = "VPCForSubnet"
        should_pass = ['module.submodule.aws_vpc.my_vpc','aws_subnet.my_subnet']
        should_fail = []
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_data_connection(self):
        root_folder = "../../../resources/s3_bucket_policy"
        check_id = "S3BucketPolicyDataSource"
        should_pass = ["aws_s3_bucket.good"]
        should_fail = ["aws_s3_bucket.bad"]
        expected_results = {check_id: {"should_pass": should_pass, "should_fail": should_fail}}

        self.run_test(root_folder=root_folder, expected_results=expected_results, check_id=check_id)

    def test_reduce_graph_by_target_types(self):
        # given
        check_id = "VPCForSubnet"
        resources_path = Path(__file__).parents[3] / "resources"
        self.runner.run(root_folder=str(resources_path), runner_filter=RunnerFilter(checks=["VPCForSubnet"]))
        graph_connector = self.runner.graph_manager.db_connector.graph
        check = next(check for check in self.registry.checks if check.id == check_id)

        # when
        reduced_graph = check.solver.reduce_graph_by_target_types(graph_connector)

        # then
        if self.graph_framework == 'NETWORKX':
            assert len(graph_connector.nodes) >= 661
            assert len(graph_connector.edges) >= 327

            assert len(reduced_graph.nodes) <= 85
            assert len(reduced_graph.edges) <= 20

        elif self.graph_framework == 'RUSTWORKX':
            assert len(graph_connector.nodes()) >= 661
            assert len(graph_connector.edges()) >= 327

            assert len(reduced_graph.nodes()) <= 85
            assert len(reduced_graph.edges()) <= 20
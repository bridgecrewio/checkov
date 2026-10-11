import os
from pathlib import Path
from unittest import TestCase

from networkx import DiGraph
from parameterized import parameterized_class
from rustworkx import PyDiGraph

from checkov.common.checks_infra.solvers.connections_solvers.connection_exists_solver import (
    ConnectionExistsSolver,
)
from checkov.common.graph.graph_builder import CustomAttributes
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


# ---------------------------------------------------------------------------
# Helpers for value-based fallback unit tests
# ---------------------------------------------------------------------------

def _make_vertex(resource_type: str, name: str, **extra: str) -> dict:
    """Build a minimal vertex dict matching the graph node schema."""
    vertex: dict = {
        CustomAttributes.RESOURCE_TYPE: resource_type,
        CustomAttributes.BLOCK_TYPE: "resource",
        "name": name,
    }
    vertex.update(extra)
    return vertex


def _build_networkx_graph(nodes: list[dict]) -> DiGraph:
    """Create a networkx DiGraph with the given node dicts (no edges)."""
    g = DiGraph()
    for idx, node in enumerate(nodes):
        g.add_node(idx, **node)
    return g


def _build_rustworkx_graph(nodes: list[dict]) -> PyDiGraph:
    """Create a rustworkx PyDiGraph with the given node dicts (no edges).

    Nodes are stored as (index, data_dict) tuples to match the real
    checkov graph format (_RustworkxGraph = PyDiGraph[tuple[int, dict], ...]).
    """
    g = PyDiGraph()
    for node in nodes:
        idx = g.add_node(None)  # placeholder
        g[idx] = (idx, node)
    return g


def _make_solver(
    resource_types: list[str],
    connected_resource_types: list[str],
) -> ConnectionExistsSolver:
    return ConnectionExistsSolver(
        resource_types=resource_types,
        connected_resources_types=connected_resource_types,
    )


# ---------------------------------------------------------------------------
# Value-based fallback tests — networkx
# ---------------------------------------------------------------------------

class TestValueBasedFallbackNetworkx(TestCase):
    """Unit tests for _value_based_fallback using networkx graphs."""

    def test_value_based_fallback_matches_by_rendered_name(self):
        """A resource whose name appears in a connected resource's attribute values should pass."""
        origin = _make_vertex("resource_type_A", "my-resource")
        connected = _make_vertex("resource_type_B", "connector", ref="my-resource")

        solver = _make_solver(["resource_type_A"], ["resource_type_B"])
        solver.vertices_under_resource_types = [origin]
        solver.vertices_under_connected_resources_types = [connected]

        graph = _build_networkx_graph([origin, connected])

        passed: list[dict] = []
        failed: list[dict] = [origin]

        solver._value_based_fallback(passed, failed, graph)

        self.assertIn(origin, passed)
        self.assertNotIn(origin, failed)

    def test_value_based_fallback_no_match_stays_failed(self):
        """A resource whose name does NOT appear in any connected resource should stay failed."""
        origin = _make_vertex("resource_type_A", "orphan-resource")
        connected = _make_vertex("resource_type_B", "connector", ref="other-resource")

        solver = _make_solver(["resource_type_A"], ["resource_type_B"])
        solver.vertices_under_resource_types = [origin]
        solver.vertices_under_connected_resources_types = [connected]

        graph = _build_networkx_graph([origin, connected])

        passed: list[dict] = []
        failed: list[dict] = [origin]

        solver._value_based_fallback(passed, failed, graph)

        self.assertNotIn(origin, passed)
        self.assertIn(origin, failed)

    def test_value_based_fallback_skips_unresolved_references(self):
        """Resources with unresolved var/module/local references should not match."""
        origin = _make_vertex("resource_type_A", "var.resource_name")
        connected = _make_vertex("resource_type_B", "connector", ref="var.resource_name")

        solver = _make_solver(["resource_type_A"], ["resource_type_B"])
        solver.vertices_under_resource_types = [origin]
        solver.vertices_under_connected_resources_types = [connected]

        graph = _build_networkx_graph([origin, connected])

        passed: list[dict] = []
        failed: list[dict] = [origin]

        solver._value_based_fallback(passed, failed, graph)

        self.assertNotIn(origin, passed)
        self.assertIn(origin, failed)

    def test_value_based_fallback_skips_empty_name(self):
        """Resources with empty name should not match."""
        origin = _make_vertex("resource_type_A", "")
        connected = _make_vertex("resource_type_B", "connector", ref="")

        solver = _make_solver(["resource_type_A"], ["resource_type_B"])
        solver.vertices_under_resource_types = [origin]
        solver.vertices_under_connected_resources_types = [connected]

        graph = _build_networkx_graph([origin, connected])

        passed: list[dict] = []
        failed: list[dict] = [origin]

        solver._value_based_fallback(passed, failed, graph)

        self.assertNotIn(origin, passed)
        self.assertIn(origin, failed)

    def test_value_based_fallback_does_not_duplicate_already_passed(self):
        """If a resource is already in passed, it should not be added again."""
        origin = _make_vertex("resource_type_A", "my-resource")
        connected = _make_vertex("resource_type_B", "connector", ref="my-resource")

        solver = _make_solver(["resource_type_A"], ["resource_type_B"])
        solver.vertices_under_resource_types = [origin]
        solver.vertices_under_connected_resources_types = [connected]

        graph = _build_networkx_graph([origin, connected])

        passed: list[dict] = [origin]
        failed: list[dict] = [origin]

        solver._value_based_fallback(passed, failed, graph)

        self.assertEqual(passed.count(origin), 1)
        self.assertNotIn(origin, failed)

    def test_value_based_fallback_ignores_connected_type_in_failed(self):
        """Only origin resource_types should be moved, not connected_resources_types."""
        origin = _make_vertex("resource_type_A", "my-resource")
        connected = _make_vertex("resource_type_B", "connector", ref="my-resource")

        solver = _make_solver(["resource_type_A"], ["resource_type_B"])
        solver.vertices_under_resource_types = [origin]
        solver.vertices_under_connected_resources_types = [connected]

        graph = _build_networkx_graph([origin, connected])

        passed: list[dict] = []
        failed: list[dict] = [connected]

        solver._value_based_fallback(passed, failed, graph)

        # connected is a connected type, not an origin type — should stay failed
        self.assertNotIn(connected, passed)
        self.assertIn(connected, failed)

    def test_value_based_fallback_handles_multiple_resources(self):
        """Multiple origin resources: matched ones pass, unmatched ones stay failed."""
        origin_a = _make_vertex("resource_type_A", "resource-a")
        origin_b = _make_vertex("resource_type_A", "resource-b")
        connected_a = _make_vertex("resource_type_B", "conn-a", ref="resource-a")

        solver = _make_solver(["resource_type_A"], ["resource_type_B"])
        solver.vertices_under_resource_types = [origin_a, origin_b]
        solver.vertices_under_connected_resources_types = [connected_a]

        graph = _build_networkx_graph([origin_a, origin_b, connected_a])

        passed: list[dict] = []
        failed: list[dict] = [origin_a, origin_b]

        solver._value_based_fallback(passed, failed, graph)

        self.assertIn(origin_a, passed)
        self.assertNotIn(origin_a, failed)
        self.assertNotIn(origin_b, passed)
        self.assertIn(origin_b, failed)

    def test_value_based_fallback_no_op_when_no_vertices(self):
        """Fallback should be a no-op when vertices lists are empty."""
        solver = _make_solver(["resource_type_A"], ["resource_type_B"])
        solver.vertices_under_resource_types = []
        solver.vertices_under_connected_resources_types = []

        graph = _build_networkx_graph([])

        passed: list[dict] = []
        failed: list[dict] = []

        solver._value_based_fallback(passed, failed, graph)

        self.assertEqual(passed, [])
        self.assertEqual(failed, [])


# ---------------------------------------------------------------------------
# Value-based fallback tests — rustworkx
# ---------------------------------------------------------------------------

class TestValueBasedFallbackRustworkx(TestCase):
    """Unit tests for _value_based_fallback using rustworkx graphs."""

    def test_value_based_fallback_matches_by_rendered_name(self):
        """A resource whose name appears in a connected resource's attribute values should pass."""
        origin = _make_vertex("resource_type_A", "my-resource")
        connected = _make_vertex("resource_type_B", "connector", ref="my-resource")

        solver = _make_solver(["resource_type_A"], ["resource_type_B"])
        solver.vertices_under_resource_types = [origin]
        solver.vertices_under_connected_resources_types = [connected]

        graph = _build_rustworkx_graph([origin, connected])

        passed: list[dict] = []
        failed: list[dict] = [origin]

        solver._value_based_fallback(passed, failed, graph)

        self.assertIn(origin, passed)
        self.assertNotIn(origin, failed)

    def test_value_based_fallback_no_match_stays_failed(self):
        """A resource whose name does NOT appear in any connected resource should stay failed."""
        origin = _make_vertex("resource_type_A", "orphan-resource")
        connected = _make_vertex("resource_type_B", "connector", ref="other-resource")

        solver = _make_solver(["resource_type_A"], ["resource_type_B"])
        solver.vertices_under_resource_types = [origin]
        solver.vertices_under_connected_resources_types = [connected]

        graph = _build_rustworkx_graph([origin, connected])

        passed: list[dict] = []
        failed: list[dict] = [origin]

        solver._value_based_fallback(passed, failed, graph)

        self.assertNotIn(origin, passed)
        self.assertIn(origin, failed)

    def test_value_based_fallback_skips_unresolved_references(self):
        """Resources with unresolved var/module/local references should not match."""
        origin = _make_vertex("resource_type_A", "module.vpc.name")
        connected = _make_vertex("resource_type_B", "connector", ref="module.vpc.name")

        solver = _make_solver(["resource_type_A"], ["resource_type_B"])
        solver.vertices_under_resource_types = [origin]
        solver.vertices_under_connected_resources_types = [connected]

        graph = _build_rustworkx_graph([origin, connected])

        passed: list[dict] = []
        failed: list[dict] = [origin]

        solver._value_based_fallback(passed, failed, graph)

        self.assertNotIn(origin, passed)
        self.assertIn(origin, failed)

    def test_value_based_fallback_handles_multiple_resources(self):
        """Multiple origin resources: matched ones pass, unmatched ones stay failed."""
        origin_a = _make_vertex("resource_type_A", "resource-a")
        origin_b = _make_vertex("resource_type_A", "resource-b")
        connected_a = _make_vertex("resource_type_B", "conn-a", ref="resource-a")

        solver = _make_solver(["resource_type_A"], ["resource_type_B"])
        solver.vertices_under_resource_types = [origin_a, origin_b]
        solver.vertices_under_connected_resources_types = [connected_a]

        graph = _build_rustworkx_graph([origin_a, origin_b, connected_a])

        passed: list[dict] = []
        failed: list[dict] = [origin_a, origin_b]

        solver._value_based_fallback(passed, failed, graph)

        self.assertIn(origin_a, passed)
        self.assertNotIn(origin_a, failed)
        self.assertNotIn(origin_b, passed)
        self.assertIn(origin_b, failed)

    def test_value_based_fallback_works_with_any_resource_types(self):
        """Fallback should work for any resource type pair, not just specific providers."""
        vpc = _make_vertex("aws_vpc", "my-vpc-id")
        subnet = _make_vertex("aws_subnet", "my-subnet", vpc_id="my-vpc-id")

        solver = _make_solver(["aws_vpc"], ["aws_subnet"])
        solver.vertices_under_resource_types = [vpc]
        solver.vertices_under_connected_resources_types = [subnet]

        graph = _build_rustworkx_graph([vpc, subnet])

        passed: list[dict] = []
        failed: list[dict] = [vpc]

        solver._value_based_fallback(passed, failed, graph)

        self.assertIn(vpc, passed)
        self.assertNotIn(vpc, failed)
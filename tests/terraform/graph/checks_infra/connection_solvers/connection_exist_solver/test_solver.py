from __future__ import annotations

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
from checkov.terraform.modules.module_objects import TFModule
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

def _make_vertex(
    resource_type: str,
    name: str,
    file_path: str = "",
    module_call: TFModule | None = None,
    **extra: str,
) -> dict:
    """Build a minimal vertex dict matching the graph node schema.

    ``module_call`` is the module call that instantiates the resource
    (``None`` for a root-level resource).
    """
    vertex: dict = {
        CustomAttributes.RESOURCE_TYPE: resource_type,
        CustomAttributes.BLOCK_TYPE: "resource",
        CustomAttributes.FILE_PATH: file_path,
        CustomAttributes.SOURCE_MODULE_OBJECT: module_call,
        "name": name,
    }
    vertex.update(extra)
    return vertex


def _module_call(root_dir: str, call_file: str, name: str, parent: TFModule | None = None) -> TFModule:
    return TFModule(path=f"{root_dir}/{call_file}", name=name, nested_tf_module=parent)


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


class _ValueBasedFallbackTests:
    """Unit tests for _value_based_fallback, run against both graph libraries."""

    build_graph = staticmethod(_build_networkx_graph)

    def _run(self, origins: list[dict], connected: list[dict], failed: list[dict], passed: list[dict] | None = None):
        solver = ConnectionExistsSolver(
            resource_types=["resource_type_A"],
            connected_resources_types=["resource_type_B"],
        )
        solver.vertices_under_resource_types = origins
        solver.vertices_under_connected_resources_types = connected
        passed = [] if passed is None else passed
        solver._value_based_fallback(passed, failed, self.build_graph(origins + connected))
        return passed, failed

    @staticmethod
    def _sibling_modules(root: str = "/project", origin_name: str = "my-resource", ref: str = "my-resource"):
        """Origin and connected resources in two sibling modules called from the same root."""
        origin = _make_vertex(
            "resource_type_A", origin_name, file_path=f"{root}/modules/origin/main.tf",
            module_call=_module_call(root, "origin.tf", "origin"),
        )
        connected = _make_vertex(
            "resource_type_B", "connector", file_path=f"{root}/modules/connected/main.tf",
            module_call=_module_call(root, "connected.tf", "connected"), ref=ref,
        )
        return origin, connected

    def test_matches_across_sibling_modules(self):
        origin, connected = self._sibling_modules()
        passed, failed = self._run([origin], [connected], [origin])
        self.assertIn(origin, passed)
        self.assertNotIn(origin, failed)

    def test_matches_module_resource_with_root_level_connected_resource(self):
        origin = _make_vertex(
            "resource_type_A", "my-resource", file_path="/project/modules/origin/main.tf",
            module_call=_module_call("/project", "main.tf", "origin"),
        )
        connected = _make_vertex("resource_type_B", "connector", file_path="/project/main.tf", ref="my-resource")
        passed, failed = self._run([origin], [connected], [origin])
        self.assertIn(origin, passed)

    def test_matches_nested_module_within_same_root(self):
        parent = _module_call("/project", "main.tf", "platform")
        origin = _make_vertex(
            "resource_type_A", "my-resource", file_path="/project/modules/network/main.tf",
            module_call=_module_call("/project/modules/platform", "main.tf", "network", parent=parent),
        )
        connected = _make_vertex(
            "resource_type_B", "connector", file_path="/project/modules/rules/main.tf",
            module_call=_module_call("/project", "rules.tf", "rules"), ref="my-resource",
        )
        passed, failed = self._run([origin], [connected], [origin])
        self.assertIn(origin, passed)

    def test_no_match_stays_failed(self):
        origin, connected = self._sibling_modules(ref="other-resource")
        passed, failed = self._run([origin], [connected], [origin])
        self.assertNotIn(origin, passed)
        self.assertIn(origin, failed)

    def test_no_match_for_root_level_resources_in_different_files(self):
        origin = _make_vertex("resource_type_A", "example", file_path="/tests/folder_a/main.tf")
        connected = _make_vertex("resource_type_B", "connector", file_path="/tests/folder_b/main.tf", ref="example")
        passed, failed = self._run([origin], [connected], [origin])
        self.assertNotIn(origin, passed)
        self.assertIn(origin, failed)

    def test_no_match_for_root_level_resources_in_same_directory(self):
        origin = _make_vertex("resource_type_A", "example", file_path="/project/a.tf")
        connected = _make_vertex("resource_type_B", "connector", file_path="/project/b.tf", ref="example")
        passed, failed = self._run([origin], [connected], [origin])
        self.assertNotIn(origin, passed)

    def test_no_match_for_modules_under_different_root_directories(self):
        origin, _ = self._sibling_modules(root="/project_a")
        _, connected = self._sibling_modules(root="/project_b")
        passed, failed = self._run([origin], [connected], [origin])
        self.assertNotIn(origin, passed)
        self.assertIn(origin, failed)

    def test_no_match_for_module_resource_and_root_resource_of_other_project(self):
        origin, _ = self._sibling_modules(root="/project_a")
        connected = _make_vertex("resource_type_B", "connector", file_path="/project_b/main.tf", ref="my-resource")
        passed, failed = self._run([origin], [connected], [origin])
        self.assertNotIn(origin, passed)

    def test_no_match_when_name_is_ambiguous_within_project(self):
        origin, connected = self._sibling_modules()
        duplicate = _make_vertex(
            "resource_type_A", "my-resource", file_path="/project/modules/other/main.tf",
            module_call=_module_call("/project", "other.tf", "other"),
        )
        passed, failed = self._run([origin, duplicate], [connected], [origin, duplicate])
        self.assertEqual(passed, [])
        self.assertEqual(failed, [origin, duplicate])

    def test_same_name_in_other_project_is_not_ambiguous(self):
        origin, connected = self._sibling_modules(root="/project_a")
        other_origin, _ = self._sibling_modules(root="/project_b")
        passed, failed = self._run([origin, other_origin], [connected], [origin, other_origin])
        self.assertEqual(passed, [origin])
        self.assertEqual(failed, [other_origin])

    def test_no_match_in_same_file(self):
        module_call = _module_call("/project", "main.tf", "combined")
        origin = _make_vertex("resource_type_A", "my-resource", file_path="/project/modules/c/main.tf", module_call=module_call)
        connected = _make_vertex(
            "resource_type_B", "connector", file_path="/project/modules/c/main.tf", module_call=module_call, ref="my-resource",
        )
        passed, failed = self._run([origin], [connected], [origin])
        self.assertNotIn(origin, passed)

    def test_skips_unresolved_references(self):
        for unresolved in ("module.vpc.name", "var.vpc_name", "local.vpc_name"):
            origin, connected = self._sibling_modules(origin_name=unresolved, ref=unresolved)
            passed, failed = self._run([origin], [connected], [origin])
            self.assertNotIn(origin, passed, unresolved)
            self.assertIn(origin, failed, unresolved)

    def test_skips_empty_name(self):
        origin, connected = self._sibling_modules(origin_name="", ref="")
        passed, failed = self._run([origin], [connected], [origin])
        self.assertNotIn(origin, passed)
        self.assertIn(origin, failed)

    def test_does_not_duplicate_already_passed(self):
        origin, connected = self._sibling_modules()
        passed, failed = self._run([origin], [connected], [origin], passed=[origin])
        self.assertEqual(passed.count(origin), 1)
        self.assertNotIn(origin, failed)

    def test_ignores_connected_type_in_failed(self):
        origin, connected = self._sibling_modules()
        connected["name"] = "my-resource"
        passed, failed = self._run([origin], [connected], [connected])
        self.assertNotIn(connected, passed)
        self.assertIn(connected, failed)

    def test_handles_multiple_resources(self):
        origin_a, connected_a = self._sibling_modules(origin_name="resource-a", ref="resource-a")
        origin_b, _ = self._sibling_modules(origin_name="resource-b", ref="resource-b")
        passed, failed = self._run([origin_a, origin_b], [connected_a], [origin_a, origin_b])
        self.assertEqual(passed, [origin_a])
        self.assertEqual(failed, [origin_b])

    def test_no_op_when_no_vertices(self):
        passed, failed = self._run([], [], [])
        self.assertEqual(passed, [])
        self.assertEqual(failed, [])


class TestValueBasedFallbackNetworkx(_ValueBasedFallbackTests, TestCase):
    build_graph = staticmethod(_build_networkx_graph)


class TestValueBasedFallbackRustworkx(_ValueBasedFallbackTests, TestCase):
    build_graph = staticmethod(_build_rustworkx_graph)

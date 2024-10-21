from pathlib import Path

from checkov.arm.graph_builder.graph_components.block_types import BlockType
from checkov.arm.graph_builder.local_graph import ArmLocalGraph
from checkov.arm.utils import get_files_definitions

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
EXPLICIT_DEPS_DIR = EXAMPLES_DIR / "ExplicitDepsResources"


def test_build_graph_with_edges():
    test_files = [EXPLICIT_DEPS_DIR / "interface.json",
                  EXPLICIT_DEPS_DIR / "storage.json",
                  EXPLICIT_DEPS_DIR / "subnet.json"]
    definitions, _, _ = get_files_definitions(test_files)
    test_graph = ArmLocalGraph(definitions)
    test_graph.build_graph()
    # TODO: Add unit tests


def test_build_graph():
    # given
    test_file = EXAMPLES_DIR / "container_instance.json"
    definitions, _, _ = get_files_definitions([str(test_file)])

    local_graph = ArmLocalGraph(definitions=definitions)

    # when
    local_graph.build_graph(render_variables=False)

    # then
    assert len(local_graph.vertices) == 15
    assert len(local_graph.edges) == 0

    assert len(local_graph.vertices_by_block_type[BlockType.PARAMETER]) == 11
    assert len(local_graph.vertices_by_block_type[BlockType.RESOURCE]) == 4

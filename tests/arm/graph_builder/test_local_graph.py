from pathlib import Path

from checkov.arm.graph_builder.graph_components.block_types import BlockType
from checkov.arm.graph_builder.local_graph import ArmLocalGraph
from checkov.arm.utils import get_files_definitions

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"
EXPLICIT_DEPS_DIR = EXAMPLES_DIR / "ExplicitDepsResources"
IMPLICIT_DEPS_DIR = EXAMPLES_DIR / "ImplicitDepsResources"


def test_graph_explicit_deps():
    test_files = [str(EXPLICIT_DEPS_DIR / "subnet.json"),
                  str(EXPLICIT_DEPS_DIR / "storage.json"),
                  str(EXPLICIT_DEPS_DIR / "interface.json")]
    definitions, _, _ = get_files_definitions(test_files)
    test_graph = ArmLocalGraph(definitions)
    test_graph.build_graph()

    assert len(test_graph.vertices) == 6
    assert len(test_graph.edges) == 5

    assert len(test_graph.vertices_by_block_type[BlockType.RESOURCE]) == 6


def test_graph_implicit_deps():
    test_files = [str(IMPLICIT_DEPS_DIR / "subnet.json"),
                  str(IMPLICIT_DEPS_DIR / "storage.json"),
                  str(IMPLICIT_DEPS_DIR / "interface.json")]
    definitions, _, _ = get_files_definitions(test_files)
    test_graph = ArmLocalGraph(definitions)
    test_graph.build_graph()

    assert len(test_graph.vertices) == 6
    assert len(test_graph.edges) == 4

    assert len(test_graph.vertices_by_block_type[BlockType.RESOURCE]) == 6

# TODO: add tests with parameters and variables vertices and rendering

from collections import Counter
from pathlib import Path

from checkov.bicep.graph_builder.graph_components.block_types import BlockType
from checkov.bicep.graph_builder.local_graph import BicepLocalGraph
from checkov.bicep.parser import Parser

EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples"


def test_build_graph():
    # given
    test_file = EXAMPLES_DIR / "playground.bicep"
    template, _ = Parser().parse(test_file)
    local_graph = BicepLocalGraph(definitions={test_file: template})

    # when
    local_graph.build_graph(render_variables=False)

    # then
    assert len(local_graph.vertices) == 24
    assert len(local_graph.edges) == 33

    assert len(local_graph.vertices_by_block_type[BlockType.TARGET_SCOPE]) == 1
    assert len(local_graph.vertices_by_block_type[BlockType.PARAM]) == 5
    assert len(local_graph.vertices_by_block_type[BlockType.VAR]) == 10
    assert len(local_graph.vertices_by_block_type[BlockType.RESOURCE]) == 8
    assert len(local_graph.vertices_by_block_type[BlockType.MODULE]) == 0
    assert len(local_graph.vertices_by_block_type[BlockType.OUTPUT]) == 0

    out_edge_counts = Counter([e.origin for e in local_graph.edges])
    in_edge_counts = Counter([e.dest for e in local_graph.edges])

    assert out_edge_counts == Counter(
        {
            16: 9,
            19: 5,
            20: 6,
            17: 3,
            18: 2,
            21: 4,
            22: 2,
            23: 2,
        }
    )
    assert in_edge_counts == Counter(
        {
            5: 8,
            6: 2,
            2: 1,
            3: 1,
            1: 1,
            20: 1,
            21: 1,
            17: 1,
            13: 1,
            4: 1,
            15: 1,
            9: 1,
            10: 2,
            11: 2,
            18: 1,
            7: 1,
            22: 1,
            23: 1,
            8: 1,
            12: 1,
            14: 1,
            19: 2,
        }
    )

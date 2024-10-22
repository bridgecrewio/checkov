from collections import Counter
from pathlib import Path

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.graph.graph_builder.graph_components.block_types import BlockType
from checkov.dockerfile.graph_builder.graph_components.resource_types import ResourceType
from checkov.dockerfile.graph_builder.local_graph import DockerfileLocalGraph
from checkov.dockerfile.runner import Runner
from checkov.dockerfile.utils import get_scannable_file_paths, get_files_definitions

RESOURCES_DIR = Path(__file__).parent.parent / "resources"


def test_build_graph():
    # given
    test_dir_path = RESOURCES_DIR / "expose_port"
    files_list = get_scannable_file_paths(root_folder=test_dir_path)
    definitions, _ = get_files_definitions(files_list)

    local_graph = DockerfileLocalGraph(definitions=definitions)

    # when
    local_graph.build_graph(render_variables=False)

    # then
    assert len(local_graph.vertices) == 16
    assert len(local_graph.edges) == 0

    assert len(local_graph.vertices_by_block_type[BlockType.RESOURCE]) == 16

    resource_type_counts = Counter(
        [vertex.attributes.get(CustomAttributes.RESOURCE_TYPE) for vertex in local_graph.vertices]
    )
    assert resource_type_counts == Counter(
        {
            ResourceType.FROM: 3,
            ResourceType.RUN: 3,
            ResourceType.EXPOSE: 3,
            ResourceType.CMD: 3,
            ResourceType.COPY: 2,
            ResourceType.WORKDIR: 1,
            ResourceType.HEALTHCHECK: 1,
        }
    )

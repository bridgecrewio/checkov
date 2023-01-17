from collections import Counter
from pathlib import Path

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.graph.graph_builder.graph_components.block_types import BlockType
from checkov.github_actions.graph_builder.graph_components.resource_types import ResourceType
from checkov.github_actions.graph_builder.local_graph import GitHubActionsLocalGraph
from checkov.github_actions.runner import Runner

RESOURCES_DIR = Path(__file__).parent.parent / "resources"


def test_build_graph():
    # given
    test_file = str(RESOURCES_DIR / ".github/workflows/supply_chain.yaml")
    template, _ = Runner()._parse_file(f=test_file)
    local_graph = GitHubActionsLocalGraph(definitions={test_file: template})

    # when
    local_graph.build_graph(render_variables=False)

    # then
    assert len(local_graph.vertices) == 6
    assert len(local_graph.edges) == 2

    assert len(local_graph.vertices_by_block_type[BlockType.RESOURCE]) == 6

    job_ids = [vertex.id for vertex in local_graph.vertices if vertex.attributes.get(CustomAttributes.RESOURCE_TYPE) == ResourceType.JOBS]
    step_ids = [vertex.id for vertex in local_graph.vertices if vertex.attributes.get(CustomAttributes.RESOURCE_TYPE) == ResourceType.STEPS]
    permission_ids = [vertex.id for vertex in local_graph.vertices if vertex.attributes.get(CustomAttributes.RESOURCE_TYPE) == ResourceType.PERMISSIONS]
    assert job_ids == ["jobs.bridgecrew", "jobs.bridgecrew2"]
    assert step_ids == ["jobs.bridgecrew.steps.1", "jobs.bridgecrew2.steps.1"]
    assert permission_ids == ["permissions"]

    out_edge_counts = Counter([e.origin for e in local_graph.edges])
    in_edge_counts = Counter([e.dest for e in local_graph.edges])

    assert out_edge_counts == Counter({0: 1, 1: 1})
    assert in_edge_counts == Counter({2: 1, 3: 1})

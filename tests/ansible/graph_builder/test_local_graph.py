from pathlib import Path

from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.graph.graph_builder.graph_components.block_types import BlockType
from checkov.ansible.graph_builder.graph_components.resource_types import ResourceType
from checkov.ansible.graph_builder.local_graph import AnsibleLocalGraph
from checkov.ansible.runner import Runner

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


def test_build_graph():
    # given
    test_file_site = str(EXAMPLES_DIR / "site.yml")
    test_file_tasks = str(EXAMPLES_DIR / "tasks.yml")
    template_site, _ = Runner()._parse_file(f=test_file_site)
    template_tasks, _ = Runner()._parse_file(f=test_file_tasks)
    local_graph = AnsibleLocalGraph(
        definitions={
            test_file_site: template_site,
            test_file_tasks: template_tasks,
        }
    )

    # when
    local_graph.build_graph(render_variables=False)

    # then
    assert len(local_graph.vertices) == 4
    assert len(local_graph.vertices_by_block_type[BlockType.RESOURCE]) == 4

    tasks_ids = [
        vertex.id
        for vertex in local_graph.vertices
        if vertex.attributes.get(CustomAttributes.RESOURCE_TYPE).startswith(ResourceType.TASKS)
    ]
    assert tasks_ids == [
        "tasks.amazon.aws.ec2_instance_info.Get Running instance Info",
        "tasks.amazon.aws.ec2_instance.enabled",
        "tasks.uri.Check that you can connect (GET) to a page",
        "tasks.ansible.builtin.get_url.Download foo.conf",
    ]

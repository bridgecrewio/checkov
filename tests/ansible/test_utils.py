from pathlib import Path

from checkov.ansible.runner import Runner
from checkov.ansible.utils import build_definitions_context, create_definitions

EXAMPLES_DIR = Path(__file__).parent / "examples"


def test_build_definitions_context():
    # given
    file_path = str(EXAMPLES_DIR / "skip.yml")
    definitions, definitions_raw = {}, {}
    definitions[file_path], definitions_raw[file_path] = Runner()._parse_file(f=file_path)

    # when
    context = build_definitions_context(definitions=definitions, definitions_raw=definitions_raw)

    assert len(context) == 1

    definition_context = next(iter(context.values()))
    assert len(definition_context) == 3

    task_context = definition_context["tasks.uri.http"]

    assert task_context["start_line"] == 24
    assert task_context["end_line"] == 31
    assert task_context["code_lines"] == [
        (24, "    - name: http\n"),
        (25, "      #checkov:skip=CKV2_ANSIBLE_1\n"),
        (26, "      uri:\n"),
        (27, "        url: http://www.example.com\n"),
        (28, "        return_content: yes\n"),
        (29, "      register: this\n"),
        (30, "      failed_when: \"'AWESOME' not in this.content\"\n"),
        (31, "\n"),
    ]

    for skip in task_context["skipped_checks"]:
        skip.pop("bc_id", None)  # depending on the test order they are set or not

    assert task_context["skipped_checks"] == [
        {
            "id": "CKV2_ANSIBLE_1",
            "line_number": 25,
            "suppress_comment": "No comment provided",
        }
    ]


def test_create_definitions():
    definitions, definitions_raw = create_definitions(root_folder=str(EXAMPLES_DIR))

    assert len(definitions) > 0
    assert all(key.endswith(".yml") or key.endswith(".yaml") and len(value) > 0 for key, value in definitions.items())
import pytest

from checkov.common.output.record import Record


@pytest.mark.parametrize(
    "input_path,expected_path",
    [
        ("s3\\main.tf", "/s3/main.tf"),
        ("s3/main.tf", "/s3/main.tf"),
        ("/abs_path/to/s3/main.tf", "/abs_path/to/s3/main.tf"),
        ("../../s3/main.tf", "/s3/main.tf"),
    ],
    ids=["windows", "rel_path", "abs_path", "recursive_rel_path"],
)
def test_determine_repo_file_path(input_path: str, expected_path: str):
    assert Record._determine_repo_file_path(input_path) == expected_path


def test_from_reduced_json(json_reduced_check):
    # Act
    record = Record.from_reduced_json(json_reduced_check)

    # Assert
    assert record.check_id == 'CKV_GHA_1'
    assert record.check_name == 'Ensure ACTIONS_ALLOW_UNSECURE_COMMANDS isn\u0027t true on environment variables'
    assert record.check_result == {
            "result": "PASSED",
            "results_configuration": {}
        }
    assert record.resource == 'jobs(container-test-job)'
    assert record.file_path == '/.github/workflows/image_no_violation.yml'
    assert record.file_line_range == [7, 7]
    assert record.file_abs_path == '/tmp/checkov/elturgeman6/elturgeman/supplygoat1/main/src/.github/workflows/image_no_violation.yml'
    assert record.code_block == [
            [
                7,
                "    runs-on: ubuntu-latest\n"
            ],
        ]
    assert record.bc_check_id == 'BC_REPO_GITHUB_ACTION_1'


def test_code_line_string_strips_control_chars():
    """Embedded ANSI/OSC escape sequences in source lines should not be passed
    through to the CLI code-block output; tab and newline must be preserved."""
    code_block = [
        (1, 'resource "x" "y" {\n'),
        (2, '\tdescription = "\x1b[2J\x1b]8;;http://example/\x07link\x1b]8;;\x07"\n'),
        (3, '}\n'),
    ]

    out = Record._code_line_string(code_block, colorized=False)

    assert "\x1b" not in out
    assert "\x07" not in out
    # printable content, tab indentation and newlines are kept
    assert "link" in out
    assert "\tdescription" in out
    assert out.count("\n") == 3

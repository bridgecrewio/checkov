from pathlib import Path

from checkov.arm.utils import get_files_definitions


def test_get_files_definitions_with_parsing_error():
    # given
    file_path = Path(__file__).parent / "parser/examples/json/with_comments.json"

    # when
    definitions, definitions_raw, parsing_errors = get_files_definitions([str(file_path)])

    # then
    assert definitions == {}
    assert definitions_raw == {}
    assert len(parsing_errors) == 1
    assert parsing_errors[0].endswith("parser/examples/json/with_comments.json")

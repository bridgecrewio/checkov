from pathlib import Path

from checkov.bicep.parser import Parser

EXAMPLES_DIR = Path(__file__).parent / "examples"


def test_parse():
    # given
    test_file = EXAMPLES_DIR / "playground.bicep"

    # when
    template, file_lines = Parser().parse(test_file)

    # then
    assert template is not None
    assert file_lines is not None

    assert len(template["parameters"]) == 5
    assert len(template["variables"]) == 10
    assert len(template["resources"]) == 8

    assert len(file_lines) == 204


def test_parse_malformed_file():
    # given
    test_file = EXAMPLES_DIR / "malformed.bicep"

    # when
    template, file_lines = Parser().parse(test_file)

    # then
    assert template is None
    assert file_lines is None

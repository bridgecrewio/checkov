from pathlib import Path

from checkov.arm.parser.parser import load, parse

EXAMPLES_DIR = Path(__file__).parent / "examples"

def test_load_mariadb():
    # given
    file_path = EXAMPLES_DIR / "json/mariadb.json"

    # when
    template, file_lines = load(file_path)

    # then
    assert template["$schema"] == "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#"
    assert template["contentVersion"] == "1.0.0.0"
    assert len(file_lines) == 25


def test_load_not_arm_file():
    # given
    file_path = EXAMPLES_DIR / "json/normal.json"

    # when
    template, file_lines = load(file_path)

    # then
    assert template == {}
    assert file_lines == []


def test_parse_arm_file_with_comments():
    # given
    file_path = EXAMPLES_DIR / "json/with_comments.json"

    # when
    template, file_lines = parse(str(file_path))

    # then
    assert template is None
    assert file_lines is None

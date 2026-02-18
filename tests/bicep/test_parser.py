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


def test_parse_with_imports():
    # given
    test_file = EXAMPLES_DIR / "imports.bicep"

    # when
    template, file_lines = Parser().parse(test_file)

    # then
    assert template is not None
    assert file_lines is not None

    # Verify imports are parsed correctly
    assert "imports" in template
    imports = template["imports"]
    assert len(imports) == 4

    # Verify individual imports
    assert "storageAccountType" in imports
    assert imports["storageAccountType"]["file_path"] == "./types.bicep"

    assert "networkConfig" in imports
    assert imports["networkConfig"]["file_path"] == "./config.bicep"

    assert "vmConfig" in imports
    assert imports["vmConfig"]["file_path"] == "./config.bicep"

    assert "securityRules" in imports
    assert imports["securityRules"]["file_path"] == "./security/rules.bicep"

    # Verify other elements are still parsed
    assert len(template["parameters"]) == 2
    assert len(template["variables"]) == 1
    assert len(template["resources"]) == 1
    assert len(template["outputs"]) == 1

    assert len(file_lines) == 27

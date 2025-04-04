from pathlib import Path

import yaml
from _pytest.logging import LogCaptureFixture

from checkov.common.checks_infra.checks_parser import GraphCheckParser
from checkov.common.checks_infra.resources_types import resources_types as raw_resources_types

EXAMPLES_DIR = Path(__file__).parent / "examples"


def test_validate_check_config(caplog: LogCaptureFixture):
    # given
    file_path = EXAMPLES_DIR / "valid_check.yaml"
    check_yaml = yaml.safe_load(file_path.read_text())

    # when
    valid = GraphCheckParser().validate_check_config(file_path=str(file_path), raw_check=check_yaml)

    # then
    assert valid
    assert len(caplog.messages) == 0


def test_validate_check_config_missing_metadata(caplog: LogCaptureFixture):
    # given
    file_path = EXAMPLES_DIR / "missing_metadata.yaml"
    check_yaml = yaml.safe_load(file_path.read_text())

    # when
    valid = GraphCheckParser().validate_check_config(file_path=str(file_path), raw_check=check_yaml)

    # then
    assert not valid
    assert caplog.messages == [
        f"Custom policy {file_path} is missing required fields metadata.id, metadata.name, metadata.category"
    ]


def test_validate_check_config_missing_metadata_category(caplog: LogCaptureFixture):
    # given
    file_path = EXAMPLES_DIR / "missing_metadata_category.yaml"
    check_yaml = yaml.safe_load(file_path.read_text())

    # when
    valid = GraphCheckParser().validate_check_config(file_path=str(file_path), raw_check=check_yaml)

    # then
    assert not valid
    assert caplog.messages == [f"Custom policy {file_path} is missing required fields metadata.category"]


def test_validate_check_config_missing_definition(caplog: LogCaptureFixture):
    # given
    file_path = EXAMPLES_DIR / "missing_definition.yaml"
    check_yaml = yaml.safe_load(file_path.read_text())

    # when
    valid = GraphCheckParser().validate_check_config(file_path=str(file_path), raw_check=check_yaml)

    # then
    assert not valid
    assert caplog.messages == [f"Custom policy {file_path} is missing required fields definition"]


def test_validate_check_config_invalid_definition(caplog: LogCaptureFixture):
    # given
    file_path = EXAMPLES_DIR / "invalid_definition.yaml"
    check_yaml = yaml.safe_load(file_path.read_text())

    # when
    valid = GraphCheckParser().validate_check_config(file_path=str(file_path), raw_check=check_yaml)

    # then
    assert not valid
    assert caplog.messages == [
        f"Custom policy {file_path} has an invalid 'definition' block type 'NoneType', "
        "needs to be either a 'list' or 'dict'"
    ]

def test_parse_taggable_resource_string():
    parser = GraphCheckParser()
    raw_check = {"resource_types": "taggable"}
    providers = ["aws"]
    check = parser._parse_raw_check(raw_check, [], providers)
    assert check.resource_types == raw_resources_types.get("aws_taggable")

def test_parse_taggable_resource_list():
    parser = GraphCheckParser()
    raw_check = {"resource_types": ["taggable"]}
    providers = ["azure"]
    check = parser._parse_raw_check(raw_check, [], providers)
    assert check.resource_types == raw_resources_types.get("azure_taggable")

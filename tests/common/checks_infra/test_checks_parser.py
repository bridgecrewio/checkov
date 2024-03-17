from pathlib import Path

import yaml
from _pytest.logging import LogCaptureFixture

from checkov.common.checks_infra.checks_parser import GraphCheckParser
from checkov.common.graph.checks_infra.enums import SolverType

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


def test__parse_raw_check_with_filter_type():
    # https://github.com/bridgecrewio/checkov/issues/5928

    # given
    raw_check = {
        "attribute": "resource_type",
        "cond_type": "filter",
        "operator": "within",
        "value": ["aws_codecommit_repository"],
    }
    resources_types = [
        "aws_root",
        "aws_root_access_key",
    ]
    providers = ["aws"]

    # when
    check = GraphCheckParser()._parse_raw_check(
        raw_check=raw_check, resources_types=resources_types, providers=providers
    )

    # then
    assert check.attribute == "resource_type"
    assert check.attribute_value == ["aws_codecommit_repository"]
    assert not check.resource_types  # this should be empty and not include 'aws_root', etc.
    assert check.type == SolverType.FILTER

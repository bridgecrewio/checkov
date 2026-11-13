import os
from pathlib import Path

import pytest
import yaml

from checkov.common.parsers.yaml.loader import SafeLineLoaderGhaSchema
from checkov.github_actions.runner import Runner
from checkov.github_actions.utils import is_schema_valid

RESOURCE_DIR = Path(__file__).parent / "resources/.github/workflows"


def test_schema_validation(bad_schema_files):
    runner = Runner()
    results = {}
    filenames = set()
    for filename in os.listdir(RESOURCE_DIR):
        f = os.path.join(RESOURCE_DIR, filename)
        filenames.add(filename)
        if os.path.isfile(f):
            res = runner._parse_file(f)
            results[filename] = True if res else False

    assert all(results[filename] is True for filename in filenames - bad_schema_files)
    assert all(results[filename] is False for filename in bad_schema_files)


def test_off_value_parsed_correctly():
    # given
    test_file = RESOURCE_DIR / "off_value.yaml"

    # when
    definition, _ = Runner()._parse_file(str(test_file))

    # then
    assert definition["jobs"]["pre-commit"]["steps"][1]["with"]["comment_mode"] is False


WORKFLOW_YAML = """
name: ci
on:
  workflow_dispatch:
    inputs:
      foo:
        description: an input
        required: false
permissions:
  contents: read
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo "${{ github.event.inputs.foo }}"
"""


@pytest.mark.parametrize("value", ["read", "write", "write-only", "none"])
def test_cache_mode_accepted_at_workflow_level(value):
    # regression test for #7786: cache-mode is a valid workflow level key
    config = yaml.load(WORKFLOW_YAML, Loader=SafeLineLoaderGhaSchema)
    config["cache-mode"] = value

    assert is_schema_valid(config) is True


@pytest.mark.parametrize("value", ["read", "write", "write-only", "none"])
def test_cache_mode_accepted_at_job_level(value):
    # regression test for #7786: cache-mode is a valid job level key
    config = yaml.load(WORKFLOW_YAML, Loader=SafeLineLoaderGhaSchema)
    config["jobs"]["build"]["cache-mode"] = value

    assert is_schema_valid(config) is True


def test_cache_mode_rejects_invalid_value():
    config = yaml.load(WORKFLOW_YAML, Loader=SafeLineLoaderGhaSchema)
    config["cache-mode"] = "bogus"
    assert is_schema_valid(config) is False

    config = yaml.load(WORKFLOW_YAML, Loader=SafeLineLoaderGhaSchema)
    config["jobs"]["build"]["cache-mode"] = "bogus"
    assert is_schema_valid(config) is False

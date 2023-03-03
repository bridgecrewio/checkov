import os
from pathlib import Path

from checkov.github_actions.runner import Runner

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

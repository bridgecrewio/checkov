from __future__ import annotations

from pathlib import Path

import pytest

from checkov.github.base_github_configuration_check import BaseGithubCheck
from checkov.common.parsers.json import parse
from checkov.json_doc.enums import BlockType

from unittest.mock import patch


@patch.multiple(BaseGithubCheck, __abstractmethods__=set())
@pytest.mark.parametrize(
    "evaluated_key,expected_conf",
    [
        ('url', 'https://api.github.com/repos/octocat/Hello-World/branches/master/protection'),
        ('required_linear_history.enabled', {'enabled': True}),
        ('required_pull_request_reviews.dismissal_restrictions.users.url',
         [{"login": "octocat", "id": 1, "url": "https://api.github.com/users/octocat"}])
    ]
)
def test_get_result_configuration(evaluated_key, expected_conf):
    # Set up test data
    base_github_check = BaseGithubCheck(
        name='Test Check',
        id='test-check',
        categories=[],
        supported_entities=[],
        block_type=BlockType.DOCUMENT,
        path=None,
        guideline=None
    )

    file_path = Path(__file__).parent / 'resources/github_conf/result_configuration/branch_protection.json'
    definitions, definitions_raw = parse(str(file_path))

    result_conf = base_github_check.get_result_configuration(evaluated_key, definitions)

    assert result_conf == expected_conf

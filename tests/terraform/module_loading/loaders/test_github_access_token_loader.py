import os
from unittest import mock

import pytest

from checkov.terraform.module_loading.loaders.github_access_token_loader import GithubAccessTokenLoader
from checkov.terraform.module_loading.module_params import ModuleParams


@pytest.mark.parametrize(
    "env, source, injected",
    [
        # VCS_ALLOWED_HOSTS not set -> unchanged behaviour (prefix match)
        ({}, "github.com/org/repo", True),
        ({}, "github.com.example.com/org/repo", True),
        # VCS_ALLOWED_HOSTS set -> GITHUB_PAT only for github.com
        ({"VCS_ALLOWED_HOSTS": "gitlab.com"}, "github.com/org/repo", True),
        ({"VCS_ALLOWED_HOSTS": "gitlab.com"}, "git::https://github.com/org/repo.git", True),
        ({"VCS_ALLOWED_HOSTS": "gitlab.com"}, "git@github.com:org/repo.git", True),
        ({"VCS_ALLOWED_HOSTS": "gitlab.com"}, "git::ssh://git@github.com/org/repo.git", True),
        ({"VCS_ALLOWED_HOSTS": "gitlab.com"}, "github.com.example.com/org/repo", False),
        ({"VCS_ALLOWED_HOSTS": "gitlab.com"}, "github.com@other.example.com/org/repo", False),
        ({"VCS_ALLOWED_HOSTS": "gitlab.com"}, "git::https://github.com.example.com/org/repo.git", False),
    ],
)
def test_github_pat_host_check(env: dict[str, str], source: str, injected: bool) -> None:
    loader = GithubAccessTokenLoader()
    module_params = ModuleParams("test", "test", source, None, "test", "test")
    with mock.patch.dict(os.environ, {"GITHUB_PAT": "ghp_test", **env}, clear=True):
        loader.discover(module_params)
        assert loader._is_matching_loader(module_params) is injected
    assert ("x-access-token:ghp_test@" in module_params.module_source) is injected

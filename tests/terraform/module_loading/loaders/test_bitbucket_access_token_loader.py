import os
from unittest import mock

import pytest

from checkov.terraform.module_loading.loaders.bitbucket_access_token_loader import BitbucketAccessTokenLoader
from checkov.terraform.module_loading.module_params import ModuleParams


@pytest.mark.parametrize(
    "env, source, injected",
    [
        # VCS_ALLOWED_HOSTS not set -> unchanged behaviour (prefix match)
        ({}, "bitbucket.org/workspace/repo.git", True),
        ({}, "bitbucket.org.example.com/workspace/repo.git", True),
        # VCS_ALLOWED_HOSTS set -> Bitbucket credentials only for bitbucket.org
        ({"VCS_ALLOWED_HOSTS": "gitlab.com"}, "bitbucket.org/workspace/repo.git", True),
        ({"VCS_ALLOWED_HOSTS": "gitlab.com"}, "bitbucket.org.example.com/workspace/repo.git", False),
        ({"VCS_ALLOWED_HOSTS": "gitlab.com"}, "bitbucket.org@other.example.com/workspace/repo.git", False),
    ],
)
def test_bitbucket_credentials_host_check(env: dict[str, str], source: str, injected: bool) -> None:
    loader = BitbucketAccessTokenLoader()
    module_params = ModuleParams("test", "test", source, None, "test", "test")
    with mock.patch.dict(os.environ, {"BITBUCKET_TOKEN": "bb_test", **env}, clear=True):
        loader.discover(module_params)
        assert loader._is_matching_loader(module_params) is True
    assert ("x-token-auth:bb_test@" in module_params.module_source) is injected

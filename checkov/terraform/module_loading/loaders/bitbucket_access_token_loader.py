from __future__ import annotations

import os
from typing import TYPE_CHECKING

from checkov.terraform.module_loading.loaders.git_loader import GenericGitLoader, get_allowed_vcs_hosts, get_source_host

if TYPE_CHECKING:
    from checkov.terraform.module_loading.module_params import ModuleParams


class BitbucketAccessTokenLoader(GenericGitLoader):
    def discover(self, module_params: ModuleParams) -> None:
        self.module_source_prefix = "bitbucket.org"
        module_params.username = os.getenv('BITBUCKET_USERNAME', '')
        app_password = os.getenv('BITBUCKET_APP_PASSWORD', '')
        module_params.token = os.getenv('BITBUCKET_TOKEN', '')
        if module_params.token:
            module_params.username = "x-token-auth"
        elif module_params.username and app_password:
            module_params.token = app_password

    def _credentials_allowed(self, module_params: ModuleParams, source: str) -> bool:
        # if VCS_ALLOWED_HOSTS is set, the Bitbucket credentials are only added for bitbucket.org
        return get_allowed_vcs_hosts() is None or get_source_host(source) == self.module_source_prefix


loader = BitbucketAccessTokenLoader()

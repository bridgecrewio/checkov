from __future__ import annotations

import os
from typing import TYPE_CHECKING

from checkov.terraform.module_loading.loaders.git_loader import GenericGitLoader

if TYPE_CHECKING:
    from checkov.terraform.module_loading.module_params import ModuleParams


class GithubAccessTokenLoader(GenericGitLoader):
    def discover(self, module_params: ModuleParams) -> None:
        self.module_source_prefix = "github.com"
        module_params.username = "x-access-token"
        module_params.token = os.getenv('GITHUB_PAT', '')

    def _is_matching_loader(self, module_params: ModuleParams) -> bool:
        if module_params.token:
            # if GITHUB_PAT is set and previous loaders failed, convert source (github ssh or github http or generic git)
            # to use the token in generic format git::https://x-access-token:<token>@github.com/org/repo.git
            self.logger.debug("GITHUB_PAT found. Attempting to clone module using HTTP basic authentication.")
            # if module_source = github.com/org/repo
            if module_params.module_source.startswith(self.module_source_prefix):
                module_params.module_source = f"git::https://{module_params.username}:{module_params.token}@{module_params.module_source}"
                return True
            # if module_source = git::https://github.com/org/repo.git
            if module_params.module_source.startswith(f"git::https://{self.module_source_prefix}"):
                module_params.module_source = f"git::https://{module_params.username}:{module_params.token}@{module_params.module_source.split('git::https://')[1]}"
                return True
            # if module_source = git@github.com:org/repo.git
            if module_params.module_source.startswith(f"git@{self.module_source_prefix}:"):
                module_params.module_source = f"git::https://{module_params.username}:{module_params.token}@{module_params.module_source.split('git@')[1].replace(':', '/')}"
                return True
            # if module_source = git::ssh://git@github.com/org/repo.git
            if module_params.module_source.startswith(f"git::ssh://git@{self.module_source_prefix}"):
                module_params.module_source = f"git::https://{module_params.username}:{module_params.token}@{module_params.module_source.split('git::ssh://git@')[1]}"
                return True

        return False


loader = GithubAccessTokenLoader()

from __future__ import annotations

from typing import TYPE_CHECKING

from checkov.terraform.module_loading.loaders.git_loader import GenericGitLoader

if TYPE_CHECKING:
    from checkov.terraform.module_loading.module_params import ModuleParams


class BitbucketLoader(GenericGitLoader):
    def discover(self, module_params: ModuleParams) -> None:
        self.module_source_prefix = "bitbucket.org"


loader = BitbucketLoader()

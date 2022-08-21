from checkov.terraform.module_loading.loaders.git_loader import GenericGitLoader
from checkov.terraform.module_loading.module_params import ModuleParams


class GithubLoader(GenericGitLoader):
    def discover(self, module_params: ModuleParams):
        self.module_source_prefix = "github.com"

    def _is_matching_loader(self, module_params: ModuleParams) -> bool:
        # https://www.terraform.io/docs/modules/sources.html#github
        if module_params.module_source.startswith(self.module_source_prefix):
            module_params.module_source = f"git::https://{module_params.module_source}"
            return True
        if module_params.module_source.startswith(f"git@{self.module_source_prefix}"):
            source = module_params.module_source.replace(":", "/")
            module_params.module_source = f"git::ssh://{source}"
            return True
        return False


loader = GithubLoader()

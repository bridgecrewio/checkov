from checkov.terraform.module_loading.loaders.git_loader import GenericGitLoader
from checkov.terraform.module_loading.module_params import ModuleParams


class BitbucketLoader(GenericGitLoader):
    def discover(self, module_params: ModuleParams):
        self.module_source_prefix = "bitbucket.org"


loader = BitbucketLoader()

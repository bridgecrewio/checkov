from checkov.common.goget.github.get_git import GitGetter
from checkov.terraform.module_loading.content import ModuleContent

from checkov.terraform.module_loading.loader import ModuleLoader
from checkov.terraform.module_loading.loaders.git_loader import GenericGitLoader


class GithubLoader(GenericGitLoader):
    def _is_matching_loader(self):
        # https://www.terraform.io/docs/modules/sources.html#github
        return 'github.com' in self.module_source


loader = GithubLoader()

import os

from checkov.common.goget.github.get_git import GitGetter
from checkov.terraform.module_loading.content import ModuleContent

from checkov.terraform.module_loading.loader import ModuleLoader


class GenericGitLoader(ModuleLoader):
    def _is_matching_loader(self):
        # https://www.terraform.io/docs/modules/sources.html#generic-git-repository
        return self.module_source.startswith('git::')

    def _load_module(self) -> ModuleContent:
        try:
            module_source = self.module_source.replace('git::', '')
            git_getter = GitGetter(module_source, create_clone_and_result_dirs=False)
            git_getter.temp_dir = self.dest_dir
            return_dir = git_getter.do_get()
            if self.inner_module:
                return_dir = os.path.join(self.dest_dir, self.inner_module)
            return ModuleContent(dir=return_dir)
        except Exception as e:
            self.logger.error(f'failed to get {self.module_source} because of {e}')
            return ModuleContent(dir=None, failed_url=self.module_source)


loader = GenericGitLoader()

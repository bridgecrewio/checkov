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
            if os.name == 'nt':
                self.logger.info(f'Operating System: {os.name}')
                self._create_valid_windows_dest_dir()
            git_getter = GitGetter(module_source, create_clone_and_result_dirs=False)
            git_getter.temp_dir = self.dest_dir
            git_getter.do_get()
            return_dir = self.dest_dir
            if self.inner_module:
                return_dir = os.path.join(self.dest_dir, self.inner_module)
            return ModuleContent(dir=return_dir)
        except Exception as e:
            self.logger.error(f'failed to get {self.module_source} because of {e}')
            return ModuleContent(dir=None, failed_url=self.module_source)

    def _create_valid_windows_dest_dir(self):
        # https://docs.microsoft.com/en-us/windows/win32/fileio/naming-a-file#naming-conventions
        reserved_windows_chars = ['<', '>', ':', '"', '|', '?', '*']
        self.logger.info(f'External module will be cloned to: {self.dest_dir}')
        for char in reserved_windows_chars:
            self.dest_dir = self.dest_dir.replace(char, '')


loader = GenericGitLoader()

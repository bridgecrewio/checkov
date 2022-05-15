from checkov.terraform.module_loading.loaders.git_loader import GenericGitLoader


class GithubLoader(GenericGitLoader):
    def discover(self):
        self.module_source_prefix = "github.com"

    def _is_matching_loader(self) -> bool:
        # https://www.terraform.io/docs/modules/sources.html#github
        if self.module_source.startswith(self.module_source_prefix):
            self.module_source = f"git::https://{self.module_source}"
            return True
        if self.module_source.startswith(f"git@{self.module_source_prefix}"):
            source = self.module_source.replace(":", "/")
            self.module_source = f"git::ssh://{source}"
            return True
        return False


loader = GithubLoader()

from checkov.terraform.module_loading.loaders.git_loader import GenericGitLoader


class GithubLoader(GenericGitLoader):
    def _is_matching_loader(self) -> bool:
        # https://www.terraform.io/docs/modules/sources.html#github
        if self.module_source.startswith("github.com"):
            self.module_source = f"git::https://{self.module_source}"
            return True
        if self.module_source.startswith("git@github.com"):
            source = self.module_source.replace(":", "/")
            self.module_source = f"git::ssh://{source}"
            return True
        return False


loader = GithubLoader()

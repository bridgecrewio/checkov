import os

from checkov.terraform.module_loading.loaders.git_loader import GenericGitLoader


class GithubAccessTokenLoader(GenericGitLoader):
    def discover(self):
        self.module_source_prefix = "github.com"
        self.username = "x-access-token"
        self.token = os.getenv('GITHUB_PAT', '')

    def _is_matching_loader(self) -> bool:
        if self.token:
            self.logger.debug("GITHUB_PAT found. Attempting to clone module using HTTP basic authentication.")
            if self.module_source.startswith(self.module_source_prefix):
                self.module_source = f"git::https://{self.username}:{self.token}@{self.module_source}"
                return True
            if self.module_source.startswith(self.module_source_prefix):
                source = self.module_source.replace(":", "/")
                self.module_source = f"git::https://{self.username}:{self.token}@{source}"
                return True

        return False


loader = GithubAccessTokenLoader()

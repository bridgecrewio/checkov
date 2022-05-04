import os

from checkov.terraform.module_loading.loaders.git_loader import GenericGitLoader


class GitlabAccessTokenLoader(GenericGitLoader):
    def discover(self):
        self.username = "x-access-token"
        self.token = os.getenv('CI_JOB_TOKEN', '')

    def _is_matching_loader(self) -> bool:
        if self.token:
            self.logger.debug("GITLAB_TOKEN found. Attempting to clone external module using token")
            if self.module_source.startswith("github.com"):
                self.module_source = f"git::https://{self.username}:{self.token}@{self.module_source}"
                return True
            if self.module_source.startswith("git@github.com"):
                source = self.module_source.replace(":", "/")
                self.module_source = f"git::https://{self.username}:{self.token}@{source}"
                return True
        return False


loader = GitlabAccessTokenLoader()

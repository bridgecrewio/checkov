import os

from checkov.terraform.module_loading.loaders.git_loader import GenericGitLoader


class BitbucketAccessTokenLoader(GenericGitLoader):
    def discover(self):
        self.username = os.getenv('BITBUCKET_USERNAME', '')
        self.app_password = os.getenv('BITBUCKET_APP_PASSWORD', '')
        self.token = os.getenv('BITBUCKET_TOKEN', '')

    def _is_matching_loader(self) -> bool:
        # https://www.terraform.io/docs/modules/sources.html#bitbucket
        if self.token:
            # https://support.atlassian.com/bitbucket-cloud/docs/use-oauth-on-bitbucket-cloud/
            if self.module_source.startswith("bitbucket.org"):
                self.module_source = f"git::https://x-token-auth:{self.token}@{self.module_source}"
                return True
        if self.username and self.app_password:
            # https://support.atlassian.com/bitbucket-cloud/docs/app-passwords/
            if self.module_source.startswith("bitbucket.org"):
                self.module_source = f"git::https://{self.username}:{self.app_password}@{self.module_source}"
                return True
        return False


loader = BitbucketAccessTokenLoader()
